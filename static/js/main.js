/* Lausanne Samstag : programme du moment.
   Données : /api/events (déjà trié et groupé par moment côté serveur).
   Préférences (Mes goûts, vue, filtres) : localStorage, sans compte. */
(() => {
    'use strict';

    const API = '/api/events';
    const RUBRIC_STYLES = {
        Concerts: 't1', 'Soirées & clubs': 't2', Scène: 't3',
        Cinéma: 't4', Expos: 't5', Autres: 't6',
    };
    const KEYS = { view: 'lc.view', tastes: 'lc.tastes', forMe: 'lc.forMe', cheap: 'lc.cheap' };

    const $ = (sel, root = document) => root.querySelector(sel);

    const store = {
        get(key, fallback) {
            try {
                const raw = localStorage.getItem(key);
                return raw === null ? fallback : JSON.parse(raw);
            } catch { return fallback; }
        },
        set(key, value) {
            try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* stockage indisponible */ }
        },
    };

    // ---------- État ----------

    const tastes = Object.assign({ rubrics: [], venues: [], onboarded: false }, store.get(KEYS.tastes, {}));
    const state = {
        data: null,
        byId: new Map(),
        moment: 'tonight',
        view: store.get(KEYS.view, 'list') === 'posters' ? 'posters' : 'list',
        forMe: store.get(KEYS.forMe, true) && tastes.rubrics.length > 0,
        cheap: false, // Prix mis de côté : ne pas réactiver un ancien filtre enregistré.
        query: '',
        revealed: new Set(),
        status: 'loading',
        controller: null,
    };

    // ---------- Outils ----------

    function h(tag, attrs = {}, ...children) {
        const node = document.createElement(tag);
        for (const [k, v] of Object.entries(attrs)) {
            if (v === null || v === undefined || v === false) continue;
            if (k === 'class') node.className = v;
            else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
            else node.setAttribute(k, v === true ? '' : v);
        }
        for (const child of children.flat()) {
            if (child === null || child === undefined || child === false) continue;
            node.append(child instanceof Node ? child : document.createTextNode(String(child)));
        }
        return node;
    }

    const fold = (s) => (s || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
    const venueKey = (evt) => fold(evt.location);
    const hasVenue = (evt) => venueKey(evt) !== '' && venueKey(evt) !== 'lausanne';
    const hasLink = (evt) => /^https?:\/\//i.test(evt.url || '');
    const tagClass = (rubric) => RUBRIC_STYLES[rubric] || 't6';

    const dayFmt = new Intl.DateTimeFormat('fr-CH', { weekday: 'long', day: 'numeric', month: 'long' });
    const shortFmt = new Intl.DateTimeFormat('fr-CH', { day: 'numeric', month: 'long' });
    const parseDay = (iso) => {
        if (!iso) return null;
        const [y, m, d] = iso.split('-').map(Number);
        return y ? new Date(y, m - 1, d) : null;
    };
    const dayLabel = (iso) => (iso ? dayFmt.format(parseDay(iso)) : 'Date non communiquée');

    function save() {
        store.set(KEYS.tastes, tastes);
        store.set(KEYS.forMe, state.forMe);
        store.set(KEYS.cheap, state.cheap);
        store.set(KEYS.view, state.view);
    }

    // ---------- Filtres ----------

    const isSmallPrice = (evt) =>
        evt.is_free || (evt.price_min !== null && evt.price_min !== undefined && evt.price_min <= state.data.small_price_chf);

    /** Masqué par Mes goûts : lieu masqué, ou rubrique hors « Pour moi ». */
    function isMasked(evt) {
        if (hasVenue(evt) && tastes.venues.includes(venueKey(evt))) return true;
        return state.forMe && tastes.rubrics.length > 0 && !tastes.rubrics.includes(evt.rubric);
    }

    /** Événements d'un jour après filtres. Les masqués sont comptés, pas oubliés. */
    function dayView(block) {
        const key = block.date || 'undated';
        const reveal = state.revealed.has(key);
        let masked = 0;
        const shown = [];
        for (const id of block.ids) {
            const evt = state.byId.get(id);
            if (!evt) continue;
            if (state.cheap && !isSmallPrice(evt)) continue;
            const m = isMasked(evt);
            if (m) masked += 1;
            if (!m || reveal) shown.push({ evt, masked: m });
        }
        return { key, date: block.date, shown, masked, reveal };
    }

    function momentCount(moment) {
        const ids = new Set();
        for (const block of moment.days) {
            for (const id of block.ids) {
                const evt = state.byId.get(id);
                if (!evt || (state.cheap && !isSmallPrice(evt)) || isMasked(evt)) continue;
                ids.add(id);
            }
        }
        return ids.size;
    }

    /** En recherche : tous les jours de tous les onglets, une seule fois. */
    function searchDays() {
        const seen = new Map();
        for (const m of state.data.moments) {
            for (const block of m.days) {
                const k = block.date || 'undated';
                if (!seen.has(k)) seen.set(k, { date: block.date, ids: [] });
                const entry = seen.get(k);
                for (const id of block.ids) if (!entry.ids.includes(id)) entry.ids.push(id);
            }
        }
        return [...seen.values()].sort((a, b) => (a.date || '9999').localeCompare(b.date || '9999'));
    }

    // ---------- Rendu : onglets et contrôles ----------

    const tabsEl = $('#tabs');
    const panel = $('#panel');

    function renderTabs() {
        tabsEl.replaceChildren(...state.data.moments.map((m) => {
            const selected = m.key === state.moment;
            return h('button', {
                type: 'button', role: 'tab', class: 'tab', id: `tab-${m.key}`,
                'aria-selected': String(selected), 'aria-controls': 'panel',
                tabindex: selected ? '0' : '-1', 'data-moment': m.key,
            }, m.label, h('small', {}, momentCount(m)));
        }));
        panel.setAttribute('aria-labelledby', `tab-${state.moment}`);
    }

    function renderControls() {
        $('#filter-forme').setAttribute('aria-pressed', String(state.forMe));
        $('#filter-cheap').setAttribute('aria-pressed', String(state.cheap));
        for (const b of document.querySelectorAll('.seg button')) {
            b.setAttribute('aria-pressed', String(b.dataset.view === state.view));
        }
    }

    // ---------- Rendu : événements ----------

    function hourCell(evt, cls = 'h') {
        return evt.time
            ? h('span', { class: cls }, evt.time)
            : h('span', { class: `${cls} nc` }, 'Heure n. c.');
    }

    function detailLine(evt, day) {
        const parts = [];
        const precision = (evt.subcategory || evt.description || '').replace(/\s+/g, ' ').trim();
        if (precision && fold(precision) !== fold(evt.title) && fold(precision) !== fold(evt.category)) {
            const excerpt = precision.length > 110
                ? `${precision.slice(0, 107).replace(/\s+\S*$/, '').trimEnd()}…` : precision;
            parts.push(excerpt);
        }
        if (evt.time_role === 'doors' && evt.time) parts.unshift(`Portes à ${evt.time}`);
        if (evt.end_date && evt.end_date !== evt.date && day) {
            parts.push(`jusqu'au ${shortFmt.format(parseDay(evt.end_date))}`);
        }
        return parts.length ? h('span', { class: 'd', title: parts.join(' · ') }, parts.join(' · ')) : null;
    }

    function eventAttrs(evt, className) {
        return { class: className, type: 'button', 'data-id': evt.id, 'aria-haspopup': 'dialog' };
    }

    function availabilityNode(evt) {
        return evt.availability === 'sold_out' ? h('span', { class: 'availability' }, 'Complet') : null;
    }

    const venueText = (evt) => (hasVenue(evt) ? evt.location : 'Lieu n. c.');

    function rowItem({ evt, masked }, day) {
        return h('li', {},
            h('button', eventAttrs(evt, `row${masked ? ' is-masked' : ''}`),
            hourCell(evt),
            h('span', {}, h('span', { class: 't' }, evt.title, null), availabilityNode(evt), detailLine(evt, day)),
            h('span', { class: 'v' }, venueText(evt))));
    }

    function tileItem({ evt, masked }) {
        const genre = evt.subcategory && evt.subcategory.length <= 22 ? evt.subcategory : '';
        const typeMedia = () => h('span', { class: 'media type' },
            h('span', { class: 'vn' }, venueText(evt)),
            genre ? h('span', { class: 'k' }, genre) : null);
        let media;
        if (evt.image) {
            const img = h('img', { src: evt.image, alt: '', loading: 'lazy', decoding: 'async' });
            media = h('span', { class: 'media' }, img, evt.time ? h('span', { class: 'st' }, `${evt.time_role === 'doors' ? 'Portes ' : ''}${evt.time}`) : null);
            img.addEventListener('error', () => {
                media.replaceWith(typeMedia());
                const t = btn.querySelector('.t');
                if (evt.time && t && !t.dataset.timed) { t.dataset.timed = '1'; t.prepend(`${evt.time_role === 'doors' ? 'Portes ' : ''}${evt.time} · `); }
            }, { once: true });
        } else {
            media = typeMedia();
        }
        const title = h('span', { class: 't' }, !evt.image && evt.time ? `${evt.time_role === 'doors' ? 'Portes ' : ''}${evt.time} · ` : '', evt.title);
        if (!evt.image && evt.time) title.dataset.timed = '1';
        const btn = h('button', eventAttrs(evt, `tile${masked ? ' is-masked' : ''}`),
        media,
        h('span', { class: 'tile-body' }, title, availabilityNode(evt), detailLine(evt, false),
            h('span', { class: 'vv' }, venueText(evt))));
        return h('li', {}, btn);
    }

    function renderDay(view) {
        const groups = new Map();
        for (const item of view.shown) {
            if (!groups.has(item.evt.rubric)) groups.set(item.evt.rubric, []);
            groups.get(item.evt.rubric).push(item);
        }
        const order = state.data.rubrics;
        const rubrics = [...groups.keys()].sort((a, b) => order.indexOf(a) - order.indexOf(b));
        const headId = `day-${view.key}`;

        const maskedNote = view.masked > 0
            ? h('p', { class: 'masked' },
                `${view.masked} masqué${view.masked > 1 ? 's' : ''} · `,
                h('button', { type: 'button', 'data-reveal': view.key, 'aria-expanded': String(view.reveal) },
                    view.reveal ? 'cacher' : 'afficher'))
            : null;

        return h('section', { class: 'day', 'aria-labelledby': headId },
            h('div', { class: 'day-head' }, h('h2', { id: headId }, dayLabel(view.date)), maskedNote),
            rubrics.map((r) => {
                const items = groups.get(r);
                return h('div', { class: 'rubric' },
                    h('h3', { class: 'rubric-head' },
                        h('span', { class: `tag ${tagClass(r)}` }, r)),
                    state.view === 'posters'
                        ? h('ul', { class: 'grid' }, items.map((it) => tileItem(it)))
                        : h('ul', { class: 'rows' }, items.map((it) => rowItem(it, view.date))));
            }));
    }

    function stateBlock(title, text, actions = []) {
        return h('div', { class: 'state' }, h('h2', {}, title), text ? h('p', {}, text) : null,
            actions.length ? h('div', { class: 'state-actions' }, actions) : null);
    }

    const actionBtn = (label, onClick, ink = false) =>
        h('button', { type: 'button', class: `btn${ink ? ' btn-ink' : ''}`, onclick: onClick }, label);

    function renderEmpty(totalMasked, rawCount) {
        if (state.query && rawCount === 0) {
            return stateBlock(`Aucun résultat pour « ${state.query} »`,
                'Vérifiez l\'orthographe ou essayez un nom de lieu.',
                [actionBtn('Effacer la recherche', () => closeSearch(true), true)]);
        }
        if (rawCount > 0) {
            const actions = [];
            if (state.cheap) actions.push(actionBtn('Retirer « Gratuit / petit prix »', () => setCheap(false), true));
            if (totalMasked > 0) actions.push(actionBtn(`Afficher les ${totalMasked} masqués`, revealAll));
            return stateBlock('Rien avec ces filtres', state.cheap
                ? 'Aucun événement gratuit ou à CHF 15 et moins, parmi ceux dont le prix est connu.'
                : 'Tout est masqué par Mes goûts.', actions);
        }
        const moment = state.data.moments.find((m) => m.key === state.moment);
        const others = state.data.moments.filter((m) => m.key !== state.moment && m.count > 0)
            .slice(0, 2)
            .map((m) => actionBtn(`${m.label} · ${momentCount(m)}`, () => selectMoment(m.key, true)));
        const label = { tonight: 'ce soir', tomorrow: 'demain', weekend: 'ce week-end', later: 'plus tard' }[moment.key];
        return stateBlock(`Rien au programme ${label}`,
            'Essayez une autre période.', others);
    }

    function render() {
        panel.setAttribute('aria-busy', String(state.status === 'loading'));
        if (state.status === 'loading') {
            panel.replaceChildren(h('div', { class: 'skeleton', 'aria-label': 'Chargement du programme' },
                h('div', { class: 'sk w1' }), ...Array.from({ length: 6 }, (_, i) => h('div', { class: `sk ${i % 2 ? 'w3' : 'w2'}` }))));
            return;
        }
        if (state.status === 'error') {
            $('#tabs-shell').hidden = !!state.query;
            panel.replaceChildren(stateBlock('Le programme n\'a pas pu être chargé',
                'Vérifiez votre connexion puis réessayez.',
                [actionBtn('Réessayer', () => load(), true)]));
            return;
        }

        const searching = !!state.query;
        $('#tabs-shell').hidden = searching;
        $('#demo-note').hidden = !state.data.demo;
        $('#onboard').hidden = tastes.onboarded || searching;
        renderTabs();
        if (searching) panel.setAttribute('aria-label', `Résultats pour ${state.query}`);
        else panel.removeAttribute('aria-label');
        if (searching) panel.removeAttribute('aria-labelledby');
        renderControls();

        const blocks = searching
            ? searchDays()
            : state.data.moments.find((m) => m.key === state.moment).days;
        const views = blocks.map(dayView);
        const visible = views.filter((v) => v.shown.length > 0);
        const totalMasked = views.reduce((n, v) => n + v.masked, 0);
        const rawCount = blocks.reduce((n, b) => n + b.ids.length, 0);

        const summary = $('#search-summary');
        const found = new Set(visible.flatMap((v) => v.shown.map((s) => s.evt.id))).size;
        summary.hidden = !searching || found === 0;
        if (searching) {
            const n = found;
            summary.replaceChildren(
                h('strong', {}, `${n} résultat${n > 1 ? 's' : ''}`), ` pour « ${state.query} » · `,
                h('button', { type: 'button', class: 'text-btn', onclick: () => closeSearch(true) }, 'Effacer'));
        }

        panel.replaceChildren(...(visible.length ? visible.map(renderDay) : [renderEmpty(totalMasked, rawCount)]));
        updateFooter();
    }

    function updateFooter() {
        const d = state.data;
        const el = $('#foot-source');
        if (d.demo) {
            el.textContent = 'Programme de démonstration : événements fictifs.';
            return;
        }
        let text = `Programme de ${d.source_count} lieux et agendas lausannois.`;
        if (d.last_update) {
            const t = new Date(d.last_update);
            text += ` Mis à jour le ${t.toLocaleDateString('fr-CH', { day: 'numeric', month: 'long' })} à ${t.toLocaleTimeString('fr-CH', { hour: '2-digit', minute: '2-digit' })}.`;
        }
        el.textContent = text;
    }

    // ---------- Actions ----------

    function selectMoment(key, focus = false) {
        state.moment = key;
        state.revealed.clear();
        render();
        if (focus) $(`#tab-${key}`)?.focus();
    }

    function setCheap(on) { state.cheap = on; save(); render(); }

    function revealAll() {
        const blocks = state.query ? searchDays() : state.data.moments.find((m) => m.key === state.moment).days;
        for (const b of blocks) state.revealed.add(b.date || 'undated');
        render();
    }

    async function load() {
        state.controller?.abort();
        const controller = new AbortController();
        state.controller = controller;
        if (!state.data) { state.status = 'loading'; render(); }
        try {
            const url = state.query ? `${API}?search=${encodeURIComponent(state.query)}` : API;
            const res = await fetch(url, { signal: controller.signal, headers: { Accept: 'application/json' } });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            state.data = data;
            state.byId = new Map(data.events.map((e) => [e.id, e]));
            state.status = 'ready';
            render();
            openFromHash();
        } catch (err) {
            if (err.name === 'AbortError') return;
            state.status = 'error';
            render();
        }
    }

    // ---------- Recherche ----------

    const searchRow = $('#search-row');
    const searchInput = $('#search-input');
    const searchToggle = $('#search-toggle');
    let searchTimer = null;

    function openSearch() {
        searchRow.hidden = false;
        searchToggle.setAttribute('aria-expanded', 'true');
        searchInput.focus();
    }

    function closeSearch(refocus = false) {
        searchRow.hidden = true;
        searchToggle.setAttribute('aria-expanded', 'false');
        searchInput.value = '';
        clearTimeout(searchTimer);
        if (state.query) { state.query = ''; load(); }
        if (refocus) searchToggle.focus();
    }

    searchToggle.addEventListener('click', () => (searchRow.hidden ? openSearch() : closeSearch(true)));
    $('#search-close').addEventListener('click', () => closeSearch(true));
    $('#search-form').addEventListener('submit', (e) => { e.preventDefault(); clearTimeout(searchTimer); runSearch(); });
    searchInput.addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(runSearch, 250); });
    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSearch(true); });

    function runSearch() {
        const q = searchInput.value.trim();
        if (q === state.query) return;
        state.query = q;
        state.revealed.clear();
        load();
    }

    // ---------- Panneaux (dialog natif : focus piégé, Échap) ----------

    let returnFocus = null;

    function openSheet(dialog, trigger = null) {
        // Safari does not necessarily focus a button when it is clicked.
        returnFocus = trigger || document.activeElement;
        dialog.showModal();
        dialog.scrollTop = 0;
        const target = dialog.querySelector('[data-autofocus]') || dialog.querySelector('.sheet-title, .ev-title');
        if (target) { target.setAttribute('tabindex', '-1'); target.focus(); }
    }

    for (const dialog of document.querySelectorAll('dialog.sheet')) {
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog || e.target.closest('[data-close]')) dialog.close();
        });
        dialog.addEventListener('close', () => {
            if (dialog.id === 'event-sheet' && location.hash.startsWith('#e=')) {
                history.replaceState(null, '', location.pathname + location.search);
            }
            const back = returnFocus && document.contains(returnFocus) ? returnFocus : null;
            const id = dialog.dataset.eventId;
            (back || (id && panel.querySelector(`[data-id="${CSS.escape(id)}"]`)) || panel).focus?.();
            returnFocus = null;
        });
    }

    // ---------- Fiche détaillée ----------

    const eventSheet = $('#event-sheet');

    function whenText(evt) {
        if (!evt.date) return h('span', { class: 'nc' }, 'Date non communiquée');
        const start = parseDay(evt.date), end = parseDay(evt.end_date);
        const next = new Date(start); next.setDate(next.getDate() + 1);
        // An overnight club occurrence is different from a multi-day programme.
        // Require the stored end instant and local date; never infer a closing time.
        const endInstant = evt.end_at ? new Date(evt.end_at) : null;
        const endHour = endInstant && !Number.isNaN(endInstant.getTime())
            ? Number(new Intl.DateTimeFormat('fr-CH', { timeZone: 'Europe/Zurich', hour: 'numeric', hourCycle: 'h23' }).formatToParts(endInstant).find(part => part.type === 'hour').value) : null;
        const overnight = evt.event_kind === 'ClubNight' && end && next.getTime() === end.getTime()
            && endHour !== null && endHour < 12;
        const multi = end && evt.end_date !== evt.date;
        const dates = multi && !overnight
            ? `Du ${shortFmt.format(start)} au ${shortFmt.format(end)}` : dayLabel(evt.date);
        const time = evt.time ? `${evt.time_role === 'doors' ? 'Portes à' : evt.rubric === 'Soirées & clubs' ? 'Dès' : 'À'} ${evt.time.replace(':', ' h ')}` : 'Heure non communiquée';
        return [h('p', { class: 'ev-date' }, dates.charAt(0).toUpperCase() + dates.slice(1)),
            h('p', { class: 'ev-time' }, time),
            overnight ? h('p', { class: 'ev-overnight' }, `Dans la nuit du ${start.getMonth() === end.getMonth() ? start.getDate() : shortFmt.format(start)} au ${shortFmt.format(end)}`) : null];
    }

    function closeEventOptions(restoreFocus = false) {
        const options = $('#event-options');
        const trigger = $('#event-options-toggle');
        if (!options || options.hidden) return;
        options.hidden = true;
        trigger?.setAttribute('aria-expanded', 'false');
        if (restoreFocus) trigger?.focus();
    }
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.ev-options, .ev-more')) closeEventOptions();
    });
    eventSheet.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && $('#event-options') && !$('#event-options').hidden) {
            e.preventDefault(); e.stopPropagation(); closeEventOptions(true);
        }
    });
    eventSheet.addEventListener('close', () => closeEventOptions());

    // Separate only explicitly recognizable metadata; never infer missing facts.
    function eventReading(evt) {
        const raw = (evt.description || '').trim();
        const film = evt.rubric === 'Cinéma' && raw.match(/^d[’'](.+?)\s+(Fiction|Documentaire|Animation),\s*([^,]+),\s*(\d{4}),\s*([^,]+),\s*(.+?),\s*(\d+\/\d+\s*ans)\s+([\s\S]+)$/i);
        let body = film ? film[8] : raw;
        // Current collectors sometimes cap prose at 400 characters. Show the last
        // complete sentence and acknowledge the missing remainder, rather than a cut word.
        const partial = raw.length === 400 && !/[.!?…][»”"')]*$/.test(raw);
        if (partial) {
            const end = Math.max(body.lastIndexOf('. '), body.lastIndexOf('! '), body.lastIndexOf('? '));
            if (end > 40) body = body.slice(0, end + 1);
            else body = body.replace(/\s+\S*$/, '') + '…';
        }
        return { film, body, partial };
    }

    function renderEventSheet(evt) {
        const venueHidden = hasVenue(evt) && tastes.venues.includes(venueKey(evt));
        const reading = eventReading(evt);
        const film = reading.film;
        const shareBtn = h('button', { type: 'button', class: 'btn', onclick: () => share(evt) }, svgIcon('share'), 'Partager');
        const linkBtn = hasLink(evt)
            ? h('a', { class: 'btn btn-ink', href: evt.url, target: '_blank', rel: 'noopener noreferrer' },
                'Voir le site', svgIcon('out'), h('span', { class: 'sr-only' }, '(nouvel onglet)'))
            : null;
        const hideBtn = hasVenue(evt)
            ? h('button', { type: 'button', class: 'ev-option ev-hide', onclick: () => {
                toggleVenue(evt);
                if (venueHidden && eventSheet.open) $('#event-options-toggle')?.focus();
            } }, venueHidden ? `Réafficher les sorties de ${evt.location}` : 'Ne plus afficher les sorties de ce lieu')
            : null;
        const moreBtn = h('button', { type: 'button', class: 'ev-more', id: 'event-options-toggle',
            'aria-label': 'Autres actions', 'aria-expanded': 'false', 'aria-controls': 'event-options',
            onclick: () => {
                const options = $('#event-options');
                const open = options.hidden;
                options.hidden = !open;
                moreBtn.setAttribute('aria-expanded', String(open));
            } }, svgIcon('more'));
        const options = h('div', { class: 'ev-options', id: 'event-options', hidden: true }, hideBtn,
            h('button', { type: 'button', class: 'ev-option ev-report', onclick: () => openFeedback(evt) }, 'Signaler une erreur'));
        const paragraphs = reading.body.split(/\n\s*\n|\n/).map(t => t.trim()).filter(Boolean);
        const visual = /^https?:\/\//i.test(evt.image || '') ? h('figure', { class: 'ev-visual' },
            h('img', { src: evt.image, alt: `Visuel de ${evt.title}`, decoding: 'async',
                onerror: () => {
                    const summary = visual.closest('.ev-summary');
                    visual.remove();
                    summary?.classList.remove('ev-has-image');
                } })) : null;
        $('#sheet-body').replaceChildren(...[
            h('header', {}, h('h2', { class: 'ev-title', id: 'sheet-title' }, evt.title),
                h('div', { class: 'ev-identity' }, h('span', { class: `tag ${tagClass(evt.rubric)}` }, evt.rubric),
                    film ? h('span', { class: 'ev-credit' }, `Un film d’${film[1]}`) : null)),
            h('section', { class: `ev-summary${visual ? ' ev-has-image' : ''}`, 'aria-label': 'Date et lieu' },
                h('div', { class: 'ev-essentials' }, whenText(evt),
                    evt.doors_time && evt.doors_time !== evt.time ? h('p', { class: 'ev-note' }, `Ouverture des portes à ${evt.doors_time}`) : null,
                    h('p', { class: 'ev-place' }, hasVenue(evt) ? evt.location : 'Lieu non communiqué'),
                    evt.room ? h('p', { class: 'ev-address' }, evt.room) : null,
                    h('p', { class: 'ev-address' }, evt.address && fold(evt.address) !== venueKey(evt) ? evt.address : 'Adresse précise à vérifier sur le site de l’événement.'),
                    availabilityNode(evt),
                    evt.access_conditions ? h('p', { class: 'ev-note' }, evt.access_conditions) : null), visual),
            film ? h('section', { class: 'ev-section ev-film-details', 'aria-label': 'Le film' },
                h('p', { class: 'ev-film' }, `${film[2]} · ${film[4]} · ${film[5]}`),
                h('p', { class: 'ev-film' }, film[3].replaceAll('/', ' / ')),
                h('p', { class: 'ev-film' }, `${film[6]} · Âge indiqué : ${film[7]}`)) : null,
            h('section', { class: 'ev-section ev-story', 'aria-label': film ? 'Synopsis' : 'Description' },
                !film && evt.subcategory && fold(evt.subcategory) !== fold(evt.description) ? h('p', { class: 'ev-kind' }, evt.subcategory) : null,
                ...paragraphs.map(t => h('p', { class: 'ev-prose' }, t)),
                !reading.body ? h('p', { class: 'ev-note' }, linkBtn
                    ? 'Description disponible sur le site de l’événement.'
                    : 'La description n’a pas été communiquée.') : null,
                reading.partial ? h('p', { class: 'ev-note' }, 'Lire la suite sur le site de l’événement.') : null),
            state.data.demo ? h('p', { class: 'ev-demo' }, 'Événement fictif (données de démonstration).') : null,
            h('footer', { class: 'ev-actions' }, linkBtn, shareBtn, moreBtn, options)
        ].filter(Boolean));
        eventSheet.dataset.eventId = evt.id;
        eventSheet.scrollTop = 0;
    }

    function openEvent(id, trigger = null) {
        const evt = state.byId.get(id);
        if (!evt) return;
        renderEventSheet(evt);
        if (location.hash !== `#e=${id}`) history.replaceState(null, '', `#e=${encodeURIComponent(id)}`);
        if (!eventSheet.open) openSheet(eventSheet, trigger);
    }

    function openFromHash() {
        const m = location.hash.match(/^#e=(.+)$/);
        if (m) {
            const id = decodeURIComponent(m[1]);
            if (!eventSheet.open || eventSheet.dataset.eventId !== id) openEvent(id);
        }
    }

    async function share(evt) {
        const url = `${location.origin}${location.pathname}#e=${encodeURIComponent(evt.id)}`;
        const when = evt.date ? `${dayLabel(evt.date)}${evt.time ? ` · ${evt.time_role === 'doors' ? 'portes à' : 'à'} ${evt.time}` : ''}` : '';
        const text = [evt.title, [when, hasVenue(evt) ? evt.location : ''].filter(Boolean).join(', ')].filter(Boolean).join(' · ');
        if (navigator.share) {
            try { await navigator.share({ title: evt.title, text, url }); return; } catch (err) {
                if (err.name === 'AbortError') return;
            }
        }
        try {
            await navigator.clipboard.writeText(url);
            toast('Lien copié');
        } catch {
            toast('Copie impossible : le lien est dans la barre d\'adresse');
        }
    }

    function svgIcon(kind) {
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('width', '16'); svg.setAttribute('height', '16'); svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none'); svg.setAttribute('stroke', 'currentColor'); svg.setAttribute('stroke-width', '2.4');
        svg.setAttribute('stroke-linecap', 'round'); svg.setAttribute('stroke-linejoin', 'round'); svg.setAttribute('aria-hidden', 'true');
        const d = kind === 'more' ? 'M4 12h.01M12 12h.01M20 12h.01' : kind === 'share' ? 'M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6' : 'M7 17 17 7M8 7h9v9';
        const path = document.createElementNS(ns, 'path');
        path.setAttribute('d', d);
        svg.append(path);
        return svg;
    }

    // ---------- Retours des testeurs ----------

    const feedbackSheet = $('#feedback-sheet');
    let feedbackEvent = null;
    function openFeedback(evt = null) {
        feedbackEvent = evt;
        $('#feedback-context').textContent = evt ? evt.title : 'Une idée ou un problème avec samstag ?';
        const eventOption = $('#feedback-kind option[value="event"]');
        eventOption.hidden = !evt;
        $('#feedback-kind').value = evt ? 'event' : 'idea';
        $('#feedback-status').textContent = '';
        $('#feedback-message').value = '';
        $('#feedback-submit').disabled = false;
        if (eventSheet.open) eventSheet.close();
        openSheet(feedbackSheet);
    }
    $('#feedback-open').addEventListener('click', () => openFeedback());
    $('#feedback-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const submit = $('#feedback-submit');
        const status = $('#feedback-status');
        submit.disabled = true;
        status.textContent = 'Envoi en cours…';
        try {
            const session = await fetch('/api/feedback/token', { credentials: 'same-origin', cache: 'no-store' });
            if (!session.ok) throw new Error('Impossible de préparer l’envoi. Réessayez.');
            const { token } = await session.json();
            const response = await fetch('/api/feedback', {
                method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, kind: $('#feedback-kind').value,
                    message: $('#feedback-message').value, event_id: feedbackEvent?.id || '' }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Envoi impossible. Réessayez.');
            status.textContent = 'Merci pour votre retour !';
            $('#feedback-message').value = '';
        } catch (err) {
            status.textContent = err instanceof TypeError ? 'Envoi interrompu. Réessayez.' : err.message;
            submit.disabled = false;
        }
    });

    // ---------- Mes goûts ----------

    function toggleVenue(evt) {
        const key = venueKey(evt);
        const wasHidden = tastes.venues.includes(key);
        tastes.venues = wasHidden ? tastes.venues.filter((v) => v !== key) : [...tastes.venues, key];
        tastes.venueNames = Object.assign({}, tastes.venueNames, { [key]: evt.location });
        save();
        if (wasHidden) {
            renderEventSheet(evt);
            render();
            toast(`${evt.location} n'est plus masqué`);
            return;
        }
        render();
        eventSheet.close();
        toast(`${evt.location} masqué`, 'Annuler', () => toggleVenue(evt));
    }

    function choiceButtons(container, selected) {
        container.replaceChildren(...state.data.rubrics.map((r) => h('button', {
            type: 'button', class: `choice ${tagClass(r)}`, 'data-rubric': r,
            'aria-pressed': String(selected.includes(r)),
            onclick: (e) => {
                const b = e.currentTarget;
                b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true'));
            },
        }, r)));
    }

    const pickedRubrics = (container) =>
        [...container.querySelectorAll('[aria-pressed="true"]')].map((b) => b.dataset.rubric);

    function applyRubrics(rubrics) {
        tastes.rubrics = rubrics;
        tastes.onboarded = true;
        state.forMe = rubrics.length > 0;
        state.revealed.clear();
        save();
        render();
    }

    const tastesSheet = $('#tastes-sheet');

    function openTastes() {
        if (!state.data) return;
        choiceButtons($('#tastes-choices'), tastes.rubrics);
        const list = $('#tastes-venues');
        const names = tastes.venueNames || {};
        list.replaceChildren(...(tastes.venues.length
            ? tastes.venues.map((key) => h('li', {}, names[key] || key,
                h('button', {
                    type: 'button', class: 'text-btn',
                    onclick: (e) => {
                        tastes.venues = tastes.venues.filter((v) => v !== key);
                        save();
                        e.currentTarget.closest('li').remove();
                        if (!tastes.venues.length) list.append(emptyVenues());
                        render();
                    },
                }, 'Afficher à nouveau')))
            : [emptyVenues()]));
        openSheet(tastesSheet);
    }

    const emptyVenues = () => h('li', { class: 'empty' }, 'Aucun lieu masqué.');

    $('#tastes-open').addEventListener('click', openTastes);
    $('#tastes-save').addEventListener('click', () => {
        applyRubrics(pickedRubrics($('#tastes-choices')));
        tastesSheet.close();
        toast(tastes.rubrics.length ? 'Préférences mises à jour' : 'Toutes les rubriques sont affichées');
    });

    $('#onboard-personalize').addEventListener('click', openTastes);
    $('#onboard-skip').addEventListener('click', () => {
        tastes.onboarded = true;
        save();
        render();
        $('#tabs')?.querySelector('[aria-selected="true"]')?.focus();
    });

    // ---------- Contrôles ----------

    $('#filter-forme').addEventListener('click', () => {
        if (!tastes.rubrics.length) { openTastes(); return; }
        state.forMe = !state.forMe;
        state.revealed.clear();
        save();
        render();
    });
    $('#filter-cheap').addEventListener('click', () => setCheap(!state.cheap));

    for (const b of document.querySelectorAll('.seg button')) {
        b.addEventListener('click', () => { state.view = b.dataset.view; save(); render(); });
    }

    tabsEl.addEventListener('click', (e) => {
        const tab = e.target.closest('[role="tab"]');
        if (tab) selectMoment(tab.dataset.moment);
    });
    tabsEl.addEventListener('keydown', (e) => {
        const keys = { ArrowRight: 1, ArrowLeft: -1, Home: -99, End: 99 };
        if (!(e.key in keys)) return;
        e.preventDefault();
        const list = state.data.moments.map((m) => m.key);
        let i = list.indexOf(state.moment) + keys[e.key];
        i = Math.max(0, Math.min(list.length - 1, e.key === 'Home' ? 0 : e.key === 'End' ? list.length - 1 : (i + list.length) % list.length));
        selectMoment(list[i], true);
    });

    panel.addEventListener('click', (e) => {
        const reveal = e.target.closest('[data-reveal]');
        if (reveal) {
            const k = reveal.dataset.reveal;
            state.revealed.has(k) ? state.revealed.delete(k) : state.revealed.add(k);
            render();
            panel.querySelector(`[data-reveal="${CSS.escape(k)}"]`)?.focus();
            return;
        }
        const card = e.target.closest('[data-id]');
        if (card) openEvent(card.dataset.id, card);
    });

    window.addEventListener('hashchange', openFromHash);

    // ---------- Toast ----------

    const toastEl = $('#toast');
    let toastTimer = null;

    function toast(message, actionLabel, onAction) {
        clearTimeout(toastTimer);
        toastEl.replaceChildren(h('span', {}, message),
            actionLabel ? h('button', {
                type: 'button',
                onclick: () => { toastEl.hidden = true; onAction(); },
            }, actionLabel) : null);
        toastEl.hidden = false;
        toastTimer = setTimeout(() => { toastEl.hidden = true; }, actionLabel ? 6000 : 3000);
    }

    // ---------- Démarrage ----------

    load();
})();
