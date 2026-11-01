const { test, expect } = require('@playwright/test');

async function ready(page) {
  await page.goto('/');
  await expect(page.locator('#panel')).toHaveAttribute('aria-busy','false');
  if (await page.getByRole('button',{name:'Pas maintenant',exact:true}).isVisible()) {
    await page.getByRole('button',{name:'Pas maintenant',exact:true}).click();
  }
}
async function findCat(page) {
  await page.getByRole('button',{name:'Rechercher',exact:true}).click();
  await page.getByRole('searchbox').fill('Cat Power');
  await expect(page.locator('#search-summary')).toContainText('1 résultat');
  return page.locator('#panel [data-id]').first();
}

test('programme réel, aucun prix ni erreur JavaScript', async ({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await ready(page);
  await expect(page.getByRole('tab')).toHaveCount(4);
  expect(await page.locator('#panel [data-id]').count()).toBeGreaterThan(0);
  await expect(page.locator('#filter-cheap')).toBeHidden();
  await expect(page.locator('#panel .price,#panel .free')).toHaveCount(0);
  expect(errors).toEqual([]);
});

test('recherche, fiche complète et destination officielle',async({page})=>{
  await ready(page);await (await findCat(page)).click();
  const sheet=page.getByRole('dialog',{name:'Cat Power',exact:true});
  await expect(sheet).toBeVisible();
  await expect(sheet).toContainText('Complet');
  await expect(sheet).toContainText('Ouverture des portes à 19:30');
  await expect(sheet).toContainText('20 h 30');
  await expect(sheet.locator('a')).toHaveAttribute('href','https://www.docks.ch/evenement/concerts/20261023/cat-power-3/');
  await expect(sheet.locator('a')).toHaveAttribute('rel',/noopener/);
  await expect(sheet.locator('.ev-prose')).toContainText('En janvier 2006');
  await sheet.getByRole('button',{name:'Fermer la fiche',exact:true}).click();
  await expect(sheet).toBeHidden();
});

test('Liste et Affiches ouvrent la même sortie',async({page})=>{
  await ready(page);const row=await findCat(page);const id=await row.getAttribute('data-id');
  await page.getByRole('button',{name:'Affiches',exact:true}).click();
  await expect(page.getByRole('button',{name:'Affiches',exact:true})).toHaveAttribute('aria-pressed','true');
  await page.locator('#panel .tile').click();
  await expect(page.locator('#event-sheet')).toHaveAttribute('data-event-id',id);
});

test('préférences enregistrées et Pour moi réversible',async({page})=>{
  await ready(page);await page.getByRole('button',{name:'Mes goûts',exact:true}).click();
  const tastes=page.locator('#tastes-sheet');
  await tastes.getByRole('button',{name:'Concerts',exact:true}).click();
  await tastes.getByRole('button',{name:'Enregistrer',exact:true}).click();
  await expect(page.locator('#filter-forme')).toHaveAttribute('aria-pressed','true');
  await page.reload();await expect(page.locator('#panel')).toHaveAttribute('aria-busy','false');
  await expect(page.locator('#filter-forme')).toHaveAttribute('aria-pressed','true');
  await page.locator('#filter-forme').click();
  await expect(page.locator('#filter-forme')).toHaveAttribute('aria-pressed','false');
  expect(await page.locator('#panel [data-id]').count()).toBeGreaterThan(0);
});

test('lieu masqué retrouvable en recherche puis restauré',async({page})=>{
  await ready(page);await (await findCat(page)).click();
  await page.getByRole('button',{name:'Autres actions',exact:true}).click();
  await page.getByRole('button',{name:'Ne plus afficher les sorties de ce lieu',exact:true}).click();
  await expect(page.locator('#panel')).toContainText('Tout est masqué');
  await page.getByRole('button',{name:'Afficher les 1 masqués',exact:true}).click();
  await page.locator('#panel [data-id]').click();
  await page.getByRole('button',{name:'Autres actions',exact:true}).click();
  await page.getByRole('button',{name:'Réafficher les sorties de Les Docks',exact:true}).click();
  await page.getByRole('button',{name:'Autres actions',exact:true}).click();
  await expect(page.getByRole('button',{name:'Ne plus afficher les sorties de ce lieu',exact:true})).toBeVisible();
});

test('avis général et signalement réellement enregistrés',async({page})=>{
  await ready(page);await page.getByRole('button',{name:'Donner mon avis',exact:true}).click();
  const dialog=page.locator('#feedback-sheet');
  await dialog.getByLabel('Votre message',{exact:true}).fill('TEST PLAYWRIGHT — avis de contrôle dans la base isolée.');
  const sent=page.waitForResponse(r=>r.url().endsWith('/api/feedback')&&r.request().method()==='POST');
  await dialog.getByRole('button',{name:'Envoyer mon retour',exact:true}).click();
  expect((await sent).status()).toBe(201);
  await expect(dialog).toContainText('Merci pour votre retour !');
  await dialog.getByRole('button',{name:'Fermer le formulaire',exact:true}).click();
  await (await findCat(page)).click();const id=await page.locator('#event-sheet').getAttribute('data-event-id');
  await page.getByRole('button',{name:'Autres actions',exact:true}).click();
  await page.getByRole('button',{name:'Signaler une erreur',exact:true}).click();
  await expect(dialog.locator('#feedback-context')).toHaveText('Cat Power');
  await dialog.getByLabel('Votre message',{exact:true}).fill('TEST PLAYWRIGHT — vérifier le contexte du signalement.');
  const request=page.waitForRequest(r=>r.url().endsWith('/api/feedback')&&r.method()==='POST');
  await dialog.getByRole('button',{name:'Envoyer mon retour',exact:true}).click();
  expect((await request).postDataJSON().event_id).toBe(id);
  await expect(dialog).toContainText('Merci pour votre retour !');
});

test('erreur réseau du formulaire : message conservé et nouvel essai possible',async({page})=>{
  await ready(page);await page.route('**/api/feedback',r=>r.abort());
  await page.getByRole('button',{name:'Donner mon avis',exact:true}).click();
  const message='TEST PLAYWRIGHT — ce texte doit survivre à la panne réseau.';
  await page.getByLabel('Votre message',{exact:true}).fill(message);
  await page.getByRole('button',{name:'Envoyer mon retour',exact:true}).click();
  await expect(page.locator('#feedback-status')).toContainText(/réessayez/i);
  await expect(page.getByLabel('Votre message',{exact:true})).toHaveValue(message);
  await expect(page.getByRole('button',{name:'Envoyer mon retour',exact:true})).toBeEnabled();
});

test('panne de programme : récupération après Réessayer',async({page})=>{
  await page.route('**/api/events',r=>r.abort());await page.goto('/');
  await expect(page.locator('#panel')).toContainText("Le programme n'a pas pu être chargé");
  await page.unroute('**/api/events');await page.getByRole('button',{name:'Réessayer',exact:true}).click();
  await expect(page.locator('#panel')).toHaveAttribute('aria-busy','false');
  expect(await page.locator('#panel [data-id]').count()).toBeGreaterThan(0);
});

test('partage avec API native simulée et lien profond',async({page})=>{
  await page.addInitScript(()=>{window.__shared=null;Object.defineProperty(navigator,'share',{configurable:true,value:async value=>{window.__shared=value;}});});
  await ready(page);await (await findCat(page)).click();const id=await page.locator('#event-sheet').getAttribute('data-event-id');
  await page.getByRole('button',{name:'Partager',exact:true}).click();
  const payload=await page.evaluate(()=>window.__shared);
  expect(payload.title).toBe('Cat Power');expect(payload.url).toContain('#e='+id);
  await page.goto(payload.url);await expect(page.getByRole('dialog',{name:'Cat Power',exact:true})).toBeVisible();
});

test('partage sans API native : copie du lien',async({page})=>{
  await page.addInitScript(()=>{window.__copied=null;Object.defineProperty(navigator,'share',{configurable:true,value:undefined});Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{window.__copied=value;}}});});
  await ready(page);await (await findCat(page)).click();await page.getByRole('button',{name:'Partager',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('Lien copié');
  expect(await page.evaluate(()=>window.__copied)).toContain('#e=');
});

test('aucun débordement horizontal à 320, 390 et 1100 px',async({page})=>{
  await ready(page);
  for(const width of [320,390,1100]){
    await page.setViewportSize({width,height:844});
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  }
  await (await findCat(page)).click();
  for(const width of [320,390,1100]){
    await page.setViewportSize({width,height:844});
    expect(await page.locator('#event-sheet').evaluate(el=>el.scrollWidth<=el.clientWidth)).toBe(true);
  }
});

test('clavier : navigation des onglets, fermeture et retour du focus',async({page})=>{
  await ready(page);await page.getByRole('tab').first().focus();
  await page.getByRole('tab').first().press('ArrowRight');
  await expect(page.getByRole('tab').nth(1)).toHaveAttribute('aria-selected','true');
  const card=await findCat(page);await card.click();await page.locator('#event-sheet').press('Escape');
  await expect(page.locator('#event-sheet')).toBeHidden();await expect(card).toBeFocused();
});
