/**
 * Patterns/Screens — compositions fidèles à trntbl.local.
 *
 * Chaque story reproduit un écran réel du portail firmware.
 * Elles servent de référence visuelle pour la QA des thèmes
 * (Sonos / Soft / Simple × Classic / Nested / Algo × modes).
 *
 * Les args contrôlent l'état dynamique (statut, panels ouverts, etc.)
 * sans dépendance au serveur Flask. Les données sont des placeholders
 * neutres — pas la vraie microcopie produit.
 */

import { devIcon, signalBars, ICONS } from './icons.js';
import { brandBlock, statusDot, check } from './primitives.js';

export default {
  title: 'Patterns/Screens',
  parameters: {
    layout: 'fullscreen',
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } },
  },
};

// ─── helpers ─────────────────────────────────────────────────────────────────

const statusBadge = (status) => {
  if (status === 'playing') {
    return `<span class="status status-play">${statusDot()}<span>Lecture en cours sur Salon — Beam</span></span>`;
  }
  return `<span class="status status-idle">${statusDot()}<span>En attente d'un vinyle</span></span>`;
};

const speakerRow = ({ icon, name, model, selected = false, disabled = false }) => `
  <button class="row"${disabled ? ' disabled' : ''}>
    ${devIcon(icon)}
    <div class="row-content">
      <div class="row-title">${name}</div>
      <div class="row-sub">${model}</div>
    </div>
    ${check({ on: selected })}
  </button>`;

const rcaRow = () => `
  <button class="row">
    ${devIcon('rca')}
    <div class="row-content">
      <div class="row-title">Sortie RCA</div>
      <div class="row-sub">Jack 3.5 mm — sun4i-codec</div>
    </div>
    ${check({ on: false })}
  </button>`;

const settingsPanel = ({ open = false, priorityActive = false } = {}) => `
  <button class="set-toggle${open ? ' active' : ''}" aria-expanded="${open}">
    <span>Réglages</span>
    <span aria-hidden="true">${open ? '▴' : '▾'}</span>
  </button>
  <div class="set-panel${open ? ' open' : ''}">

    <div class="set-section">
      <div class="set-section-title">Qualité audio</div>
      <div class="seg-track" role="group" aria-label="Qualité audio">
        <button class="seg-segment" aria-pressed="false">128k</button>
        <button class="seg-segment" aria-pressed="false">192k</button>
        <button class="seg-segment active" aria-pressed="true">256k</button>
        <button class="seg-segment" aria-pressed="false">320k</button>
      </div>
      <div class="toggle-row">
        <span class="toggle-label" aria-hidden="true">Afficher la sortie RCA</span>
        <label class="toggle-switch">
          <input type="checkbox" aria-label="Afficher la sortie RCA">
          <span class="toggle-slider" aria-hidden="true"></span>
        </label>
      </div>
    </div>

    <div class="set-section">
      <div class="set-section-title">Affichage</div>
      <div class="set-row">
        <span class="set-row-label">Thème</span>
        <div class="seg-track" role="group" aria-label="Thème">
          <button class="seg-segment active" aria-pressed="true">Sonos</button>
          <button class="seg-segment" aria-pressed="false">Soft</button>
          <button class="seg-segment" aria-pressed="false">Simple</button>
        </div>
      </div>
      <div class="set-row">
        <span class="set-row-label">Apparence</span>
        <div class="seg-track" role="group" aria-label="Apparence">
          <button class="seg-segment active" aria-pressed="true">Auto</button>
          <button class="seg-segment" aria-pressed="false">Clair</button>
          <button class="seg-segment" aria-pressed="false">Sombre</button>
        </div>
      </div>
      <div class="set-row">
        <span class="set-row-label">Densité</span>
        <div class="seg-track" role="group" aria-label="Densité">
          <button class="seg-segment" aria-pressed="false">Compact</button>
          <button class="seg-segment active" aria-pressed="true">Standard</button>
          <button class="seg-segment" aria-pressed="false">Aéré</button>
        </div>
      </div>
      <div class="set-row">
        <span class="set-row-label">Contraste élevé</span>
        <div class="seg-track" role="group" aria-label="Contraste élevé">
          <button class="seg-segment active" aria-pressed="true">Off</button>
          <button class="seg-segment" aria-pressed="false">On</button>
        </div>
      </div>
      <div class="set-row">
        <span class="set-row-label">Vision</span>
        <div class="seg-track" role="group" aria-label="Vision">
          <button class="seg-segment active" aria-pressed="true">Auto</button>
          <button class="seg-segment" aria-pressed="false">Deutan</button>
          <button class="seg-segment" aria-pressed="false">Protan</button>
          <button class="seg-segment" aria-pressed="false">Tritan</button>
          <button class="seg-segment" aria-pressed="false">Achroma</button>
        </div>
      </div>
    </div>

    <div class="set-section">
      <div class="set-section-title">Langue</div>
      <div class="seg-track" role="group" aria-label="Langue">
        <button class="seg-segment active" aria-pressed="true">Auto</button>
        <button class="seg-segment" aria-pressed="false">FR</button>
        <button class="seg-segment" aria-pressed="false">EN</button>
        <button class="seg-segment" aria-pressed="false">ES</button>
      </div>
    </div>

    <div class="set-section">
      <div class="set-section-title">À propos</div>
      <div class="set-info">
        openTRNTBL v1.0.0-alpha<br>
        CHIP • Debian Jessie • Python 2.7<br>
        hw:1,0 — PCM2900C 48 kHz
      </div>
    </div>

    <button class="btn btn-2">Changer de réseau WiFi</button>
    <button class="btn btn-disconnect">Déconnecter du WiFi</button>
  </div>`;

// ─── Story : Dashboard ────────────────────────────────────────────────────────

export const Dashboard = {
  name: 'Dashboard',
  parameters: {
    controls: { disable: false },
    docs: { description: { story: 'Écran principal du portail — état complet avec enceintes, flux, réglages. Switcher de thème visible dans le panel Réglages.' } },
  },
  args: {
    status:        'playing',
    settingsOpen:  false,
    priorityActive: false,
    rcaVisible:    false,
  },
  argTypes: {
    status:        { control: 'select', options: ['idle', 'playing'], description: 'État du flux vinyle' },
    settingsOpen:  { control: 'boolean', description: 'Panel Réglages ouvert' },
    priorityActive: { control: 'boolean', description: 'Priorité vinyle activée' },
    rcaVisible:    { control: 'boolean', description: 'Sortie RCA affichée' },
  },
  render: ({ status, settingsOpen, priorityActive, rcaVisible }) => `
    <div class="page dash-page">

      <section class="dash-zone zone-header">
        ${brandBlock()}
      </section>

      <section class="dash-zone zone-top">
        <h1 class="title">Platine</h1>
        <div class="status-wrap">${statusBadge(status)}</div>
        <div class="wifi-bar">${signalBars(3)}<span>MyHomeWiFi</span></div>
      </section>

      ${rcaVisible ? `
      <section class="dash-zone zone-output">
        <h2 class="section">Sortie locale</h2>
        <div class="card">${rcaRow()}</div>
      </section>` : ''}

      <section class="dash-zone zone-speakers">
        <h2 class="section">Enceintes Sonos</h2>
        <div class="card">
          ${speakerRow({ icon: 'soundbar', name: 'Salon — Beam',   model: 'Sonos Beam Gen 2',  selected: true })}
          ${speakerRow({ icon: 'compact',  name: 'Chambre',        model: 'Sonos Era 100',      selected: false })}
          ${speakerRow({ icon: 'portable', name: 'Cuisine',        model: 'Sonos Roam',         selected: false })}
          ${speakerRow({ icon: 'large',    name: 'Salon — One',    model: 'Sonos One',          selected: true })}
        </div>
        <div class="zone-actions">
          <button class="btn-ghost">Rescanner</button>
          <button class="btn btn-disconnect">Tout déconnecter</button>
          <button class="btn btn-toggle${priorityActive ? ' active' : ''}">
            ${priorityActive ? 'Priorité active' : 'Activer la priorité'}
          </button>
        </div>
      </section>

      <section class="dash-zone zone-stream">
        <h2 class="section">Flux audio</h2>
        <div class="card"><div class="stream-card">
          <div class="stream-label">Partagez ce lien pour écouter depuis un navigateur ou un lecteur média</div>
          <div class="stream-row">
            <div class="stream-url">http://trntbl.local:8000/vinyl</div>
            <button class="btn-tonal">Partager</button>
          </div>
        </div></div>
      </section>

      <section class="dash-zone zone-settings">
        ${settingsPanel({ open: settingsOpen, priorityActive })}
      </section>

    </div>
  `,
};

// ─── Story : Dashboard — réglages ouverts ─────────────────────────────────────

export const DashboardSettings = {
  name: 'Dashboard — Réglages',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Dashboard avec le panel Réglages ouvert — QA du theme switcher (Sonos/Soft/Simple × Classic/Nested/Algo) et des axes a11y.' } },
  },
  render: () => `
    <div class="page dash-page">

      <section class="dash-zone zone-header">
        ${brandBlock()}
      </section>

      <section class="dash-zone zone-top">
        <h1 class="title">Platine</h1>
        <div class="status-wrap">${statusBadge('idle')}</div>
        <div class="wifi-bar">${signalBars(4)}<span>MyHomeWiFi</span></div>
      </section>

      <section class="dash-zone zone-speakers">
        <h2 class="section">Enceintes Sonos</h2>
        <div class="card">
          ${speakerRow({ icon: 'soundbar', name: 'Salon — Beam', model: 'Sonos Beam Gen 2', selected: false })}
          ${speakerRow({ icon: 'compact',  name: 'Chambre',      model: 'Sonos Era 100',    selected: false })}
        </div>
        <div class="zone-actions">
          <button class="btn-ghost">Rescanner</button>
          <button class="btn btn-toggle">Activer la priorité</button>
        </div>
      </section>

      <section class="dash-zone zone-settings">
        ${settingsPanel({ open: true })}
      </section>

    </div>
  `,
};

// ─── Story : WiFi setup ───────────────────────────────────────────────────────

export const WifiSetup = {
  name: 'WiFi setup',
  parameters: {
    controls: { disable: false },
    docs: { description: { story: 'Écran de configuration WiFi — liste des réseaux, saisie du mot de passe, réglages a11y + theme switcher.' } },
  },
  args: {
    settingsOpen: false,
  },
  argTypes: {
    settingsOpen: { control: 'boolean', description: 'Panel Réglages ouvert' },
  },
  render: ({ settingsOpen }) => `
    <div class="page">
      ${brandBlock()}
      <h1 class="title">WiFi</h1>
      <p class="subtitle">Connectez votre platine pour diffuser vos vinyles.</p>

      <div style="display:flex;justify-content:space-between;align-items:center;gap:var(--spacing-default);margin:24px 0 12px">
        <h2 class="section" style="margin:0">Réseaux disponibles</h2>
        <button class="btn-tonal" style="flex-shrink:0">Rescanner</button>
      </div>

      <div class="card" role="group" aria-label="Réseaux disponibles">
        <button class="row">
          <div class="row-content"><div class="row-title">MyHomeWiFi</div></div>
          <div class="row-right">
            <span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>
            ${signalBars(4)}
            <span class="chevron" aria-hidden="true">›</span>
          </div>
        </button>
        <button class="row">
          <div class="row-content"><div class="row-title">Livebox-XXXX</div></div>
          <div class="row-right">
            <span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>
            ${signalBars(2)}
            <span class="chevron" aria-hidden="true">›</span>
          </div>
        </button>
        <button class="row">
          <div class="row-content"><div class="row-title">FreeWifi_secure</div></div>
          <div class="row-right">
            ${signalBars(1)}
            <span class="chevron" aria-hidden="true">›</span>
          </div>
        </button>
      </div>

      <div style="margin:var(--spacing-default) 0">
        <h2 class="section" style="margin-bottom:var(--spacing-snug)">Mot de passe</h2>
        <div class="card"><div class="inp-group">
          <label class="inp-label" for="wifi-pw-mock">MyHomeWiFi</label>
          <div class="inp-wrap">
            <input class="inp inp-pw" id="wifi-pw-mock" type="password" placeholder="Mot de passe" value="••••••••••">
            <button class="inp-action" aria-label="Afficher le mot de passe">Afficher</button>
          </div>
        </div></div>
      </div>

      <button class="btn btn-1">Connecter</button>

      <button class="set-toggle${settingsOpen ? ' active' : ''}" aria-expanded="${settingsOpen}">
        <span>Réglages</span>
        <span aria-hidden="true">${settingsOpen ? '▴' : '▾'}</span>
      </button>
      <div class="set-panel${settingsOpen ? ' open' : ''}">

        <div class="set-section">
          <div class="set-section-title">Style</div>
          <div class="set-row">
            <span class="set-row-label">Thème visuel</span>
            <div class="seg-track" role="group" aria-label="Thème visuel">
              <button class="seg-segment active" aria-pressed="true">Sonos</button>
              <button class="seg-segment" aria-pressed="false">Soft</button>
              <button class="seg-segment" aria-pressed="false">Simple</button>
            </div>
          </div>
        </div>

        <div class="set-section">
          <div class="set-section-title">Affichage</div>
          <div class="set-row">
            <span class="set-row-label">Thème</span>
            <div class="seg-track" role="group" aria-label="Thème">
              <button class="seg-segment active" aria-pressed="true">Sonos</button>
              <button class="seg-segment" aria-pressed="false">Soft</button>
              <button class="seg-segment" aria-pressed="false">Simple</button>
            </div>
          </div>
          <div class="set-row">
            <span class="set-row-label">Apparence</span>
            <div class="seg-track" role="group" aria-label="Apparence">
              <button class="seg-segment active" aria-pressed="true">Auto</button>
              <button class="seg-segment" aria-pressed="false">Clair</button>
              <button class="seg-segment" aria-pressed="false">Sombre</button>
            </div>
          </div>
          <div class="set-row">
            <span class="set-row-label">Densité</span>
            <div class="seg-track" role="group" aria-label="Densité">
              <button class="seg-segment" aria-pressed="false">Compact</button>
              <button class="seg-segment active" aria-pressed="true">Standard</button>
              <button class="seg-segment" aria-pressed="false">Aéré</button>
            </div>
          </div>
          <div class="set-row">
            <span class="set-row-label">Contraste élevé</span>
            <div class="seg-track" role="group" aria-label="Contraste élevé">
              <button class="seg-segment active" aria-pressed="true">Off</button>
              <button class="seg-segment" aria-pressed="false">On</button>
            </div>
          </div>
          <div class="set-row">
            <span class="set-row-label">Vision</span>
            <div class="seg-track" role="group" aria-label="Vision">
              <button class="seg-segment active" aria-pressed="true">Auto</button>
              <button class="seg-segment" aria-pressed="false">Deutan</button>
              <button class="seg-segment" aria-pressed="false">Protan</button>
              <button class="seg-segment" aria-pressed="false">Tritan</button>
              <button class="seg-segment" aria-pressed="false">Achroma</button>
            </div>
          </div>
        </div>

        <div class="set-section">
          <div class="set-section-title">Langue</div>
          <div class="seg-track" role="group" aria-label="Langue">
            <button class="seg-segment active" aria-pressed="true">Auto</button>
            <button class="seg-segment" aria-pressed="false">FR</button>
            <button class="seg-segment" aria-pressed="false">EN</button>
            <button class="seg-segment" aria-pressed="false">ES</button>
          </div>
        </div>

      </div>
    </div>
  `,
};

// ─── Story : Reconnexion perdue ───────────────────────────────────────────────

export const ConnectionLost = {
  name: 'Connection lost',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Écran d\'erreur réseau — alert warning + spinner de reconnexion.' } },
  },
  render: () => `
    <div class="page">
      ${brandBlock()}
      <h1 class="title">Connexion</h1>
      <div style="height:16px"></div>
      <div class="alert warning" role="alert">
        <div class="alert-icon">
          <svg viewBox="0 0 24 24"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="alert-content">
          <div class="alert-body">Le réseau <strong>MyHomeWiFi</strong> n'est pas accessible.<br>Vérifiez que votre box est allumée.</div>
        </div>
      </div>
      <div class="reconnect">
        <div class="spin"></div>
        <div style="font-size:14px;color:var(--text-color-secondary)">Reconnexion automatique…</div>
      </div>
      <div style="height:8px"></div>
      <button class="btn btn-2">Changer de réseau</button>
    </div>
  `,
};
