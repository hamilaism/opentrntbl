/**
 * openTRNTBL — i18n (FR / EN / ES)
 *
 * Tiny no-framework i18n layer. Inlined into firmware/index.html on serve.
 * No build step, no fetch, no network — runs offline on the CHIP.
 *
 * Usage in HTML : <span data-i18n="wifi.connect">Connecter</span>
 *                  (the inner text is the FR fallback if i18n.js fails to load)
 * Usage in JS  : t('wifi.connect')   →  "Connecter" (FR) / "Connect" (EN) / "Conectar" (ES)
 *
 * Locale detection order:
 * 1. localStorage('opentrntbl-lang') — user explicit choice
 * 2. navigator.language prefix (e.g. 'es-AR' → 'es', 'en-US' → 'en')
 * 3. fallback 'fr' (current default product language)
 *
 * Switcher: ui-rendered in Settings panel via #lang-switcher.
 */

var I18N = {
  fr: {
    'app.title':           'openTRNTBL',
    'wifi.title':          'WiFi',
    'wifi.subtitle':       'Connectez votre platine pour diffuser vos vinyles.',
    'wifi.networks':       'Réseaux disponibles',
    'wifi.rescan':         'Rescanner',
    'wifi.manual':         'Saisir manuellement',
    'wifi.ssid':           'Nom du réseau',
    'wifi.password':       'Mot de passe',
    'wifi.show':           'Afficher',
    'wifi.hide':           'Masquer',
    'wifi.connect':        'Connecter',
    'wifi.connecting':     'Connexion…',
    'wifi.connection_title':'Connexion',
    'wifi.connected_ok':   '✓ Connecté — redémarrage…',
    'wifi.connect_fail':   'Connexion échouée.',
    'wifi.error':          'Erreur.',
    'wifi.unreachable_pre':'Le réseau ',
    'wifi.unreachable_post':' n\'est pas accessible.',
    'wifi.check_router':   'Vérifiez que votre box est allumée.',
    'wifi.reconnecting':   'Reconnexion automatique…',
    'wifi.change_network': 'Changer de réseau',
    'wifi.disconnect':     'Déconnecter du WiFi',
    'wifi.confirm_reset':  'Le TRNTBL va redémarrer en mode configuration (AP TRNTBL-Setup). Continuer ?',
    'wifi.rebooting':      'Redémarrage en mode configuration',
    'wifi.switching_to_setup':'Bascule en mode configuration',
    'wifi.connect_setup_ap':'Connecte-toi au WiFi TRNTBL-Setup dans ~30s.',

    'dash.title':          'Platine',
    'dash.idle':           "En attente d'un vinyle",
    'dash.playing_on':     'En lecture sur ',
    'dash.partial_on':     'Lecture partielle · ',
    'dash.taken_other':    ' · autre source',
    'dash.unreachable':    'Enceinte injoignable',
    'dash.connecting':     'Connexion en cours…',
    'dash.local_output':   'Sortie locale',
    'dash.sonos_speakers': 'Enceintes Sonos',
    'dash.disconnect_all': 'Tout déconnecter',
    'dash.priority_on':    'Activer la priorité',
    'dash.priority_off':   'Désactiver la priorité',
    'dash.audio_stream':   'Flux audio',
    'dash.share_hint':     'Partagez ce lien pour écouter depuis un navigateur ou un lecteur média',
    'dash.share':          'Partager',
    'dash.copied':         'Copié !',
    'dash.share_title':    'openTRNTBL',
    'dash.share_text':     'Écoute mon vinyle en direct',
    'dash.copy_prompt':    'Copiez ce lien :',

    'settings.title':      'Réglages',
    'settings.audio_quality':'Qualité audio',
    'settings.show_rca':   'Afficher la sortie RCA',
    'settings.rca_visible':'Sortie RCA visible',
    'settings.network':    'Réseau',
    'settings.ip':         'IP',
    'settings.version':    'Version',
    'settings.uptime':     'Uptime',
    'settings.language':   'Langue',
    'settings.display':    'Affichage',
    'settings.theme':      'Thème',
    'settings.theme_auto': 'Auto',
    'settings.theme_light':'Clair',
    'settings.theme_dark': 'Sombre',
    'settings.density':    'Densité',
    'settings.density_compact':'Compact',
    'settings.density_default':'Standard',
    'settings.density_spacious':'Aéré',
    'settings.contrast':   'Contraste élevé',
    'settings.contrast_off':'Off',
    'settings.contrast_on':'On',
    'settings.vision':     'Vision',
    'settings.vision_default':'Auto',
    'settings.vision_deutan':'Deutan',
    'settings.vision_protan':'Protan',
    'settings.vision_tritan':'Tritan',
    'settings.vision_achroma':'Achroma',
    'settings.lang_auto':  'Auto',
    'settings.about':      'À propos',

    'rca.label':           'RCA local',
    'common.search':       'Recherche en cours…',
    'common.no_networks':  'Aucun réseau trouvé',
    'common.scan_running': 'Scan en cours…',
    'common.back':         '← Retour',
  },

  en: {
    'app.title':           'openTRNTBL',
    'wifi.title':          'WiFi',
    'wifi.subtitle':       'Connect your turntable to stream your vinyl.',
    'wifi.networks':       'Available networks',
    'wifi.rescan':         'Rescan',
    'wifi.manual':         'Enter manually',
    'wifi.ssid':           'Network name',
    'wifi.password':       'Password',
    'wifi.show':           'Show',
    'wifi.hide':           'Hide',
    'wifi.connect':        'Connect',
    'wifi.connecting':     'Connecting…',
    'wifi.connection_title':'Connection',
    'wifi.connected_ok':   '✓ Connected — restarting…',
    'wifi.connect_fail':   'Connection failed.',
    'wifi.error':          'Error.',
    'wifi.unreachable_pre':'The network ',
    'wifi.unreachable_post':' is unreachable.',
    'wifi.check_router':   'Make sure your router is on.',
    'wifi.reconnecting':   'Auto-reconnecting…',
    'wifi.change_network': 'Change network',
    'wifi.disconnect':     'Disconnect from WiFi',
    'wifi.confirm_reset':  'TRNTBL will restart in configuration mode (AP TRNTBL-Setup). Continue?',
    'wifi.rebooting':      'Restarting in configuration mode',
    'wifi.switching_to_setup':'Switching to configuration mode',
    'wifi.connect_setup_ap':'Connect to the TRNTBL-Setup WiFi in ~30s.',

    'dash.title':          'Turntable',
    'dash.idle':           'Waiting for a vinyl',
    'dash.playing_on':     'Playing on ',
    'dash.partial_on':     'Partial playback · ',
    'dash.taken_other':    ' · other source',
    'dash.unreachable':    'Speaker unreachable',
    'dash.connecting':     'Connecting…',
    'dash.local_output':   'Local output',
    'dash.sonos_speakers': 'Sonos speakers',
    'dash.disconnect_all': 'Disconnect all',
    'dash.priority_on':    'Enable priority',
    'dash.priority_off':   'Disable priority',
    'dash.audio_stream':   'Audio stream',
    'dash.share_hint':     'Share this link to listen from a browser or media player',
    'dash.share':          'Share',
    'dash.copied':         'Copied!',
    'dash.share_title':    'openTRNTBL',
    'dash.share_text':     'Listen to my vinyl live',
    'dash.copy_prompt':    'Copy this link:',

    'settings.title':      'Settings',
    'settings.audio_quality':'Audio quality',
    'settings.show_rca':   'Show RCA output',
    'settings.rca_visible':'RCA output visible',
    'settings.network':    'Network',
    'settings.ip':         'IP',
    'settings.version':    'Version',
    'settings.uptime':     'Uptime',
    'settings.language':   'Language',
    'settings.display':    'Display',
    'settings.theme':      'Theme',
    'settings.theme_auto': 'Auto',
    'settings.theme_light':'Light',
    'settings.theme_dark': 'Dark',
    'settings.density':    'Density',
    'settings.density_compact':'Compact',
    'settings.density_default':'Default',
    'settings.density_spacious':'Spacious',
    'settings.contrast':   'High contrast',
    'settings.contrast_off':'Off',
    'settings.contrast_on':'On',
    'settings.vision':     'Vision',
    'settings.vision_default':'Auto',
    'settings.vision_deutan':'Deutan',
    'settings.vision_protan':'Protan',
    'settings.vision_tritan':'Tritan',
    'settings.vision_achroma':'Achroma',
    'settings.lang_auto':  'Auto',
    'settings.about':      'About',

    'rca.label':           'Local RCA',
    'common.search':       'Searching…',
    'common.no_networks':  'No networks found',
    'common.scan_running': 'Scan in progress…',
    'common.back':         '← Back',
  },

  es: {
    'app.title':           'openTRNTBL',
    'wifi.title':          'WiFi',
    'wifi.subtitle':       'Conecta tu tocadiscos para emitir tu vinilo.',
    'wifi.networks':       'Redes disponibles',
    'wifi.rescan':         'Reescanear',
    'wifi.manual':         'Introducir manualmente',
    'wifi.ssid':           'Nombre de la red',
    'wifi.password':       'Contraseña',
    'wifi.show':           'Mostrar',
    'wifi.hide':           'Ocultar',
    'wifi.connect':        'Conectar',
    'wifi.connecting':     'Conectando…',
    'wifi.connection_title':'Conexión',
    'wifi.connected_ok':   '✓ Conectado — reiniciando…',
    'wifi.connect_fail':   'Conexión fallida.',
    'wifi.error':          'Error.',
    'wifi.unreachable_pre':'La red ',
    'wifi.unreachable_post':' no es accesible.',
    'wifi.check_router':   'Comprueba que tu router esté encendido.',
    'wifi.reconnecting':   'Reconectando automáticamente…',
    'wifi.change_network': 'Cambiar de red',
    'wifi.disconnect':     'Desconectar del WiFi',
    'wifi.confirm_reset':  'TRNTBL se reiniciará en modo configuración (AP TRNTBL-Setup). ¿Continuar?',
    'wifi.rebooting':      'Reiniciando en modo configuración',
    'wifi.switching_to_setup':'Cambiando al modo configuración',
    'wifi.connect_setup_ap':'Conéctate al WiFi TRNTBL-Setup en ~30s.',

    'dash.title':          'Tocadiscos',
    'dash.idle':           'Esperando un vinilo',
    'dash.playing_on':     'Reproduciendo en ',
    'dash.partial_on':     'Reproducción parcial · ',
    'dash.taken_other':    ' · otra fuente',
    'dash.unreachable':    'Altavoz no disponible',
    'dash.connecting':     'Conectando…',
    'dash.local_output':   'Salida local',
    'dash.sonos_speakers': 'Altavoces Sonos',
    'dash.disconnect_all': 'Desconectar todo',
    'dash.priority_on':    'Activar prioridad',
    'dash.priority_off':   'Desactivar prioridad',
    'dash.audio_stream':   'Flujo de audio',
    'dash.share_hint':     'Comparte este enlace para escucharlo desde un navegador o reproductor',
    'dash.share':          'Compartir',
    'dash.copied':         '¡Copiado!',
    'dash.share_title':    'openTRNTBL',
    'dash.share_text':     'Escucha mi vinilo en vivo',
    'dash.copy_prompt':    'Copia este enlace:',

    'settings.title':      'Ajustes',
    'settings.audio_quality':'Calidad de audio',
    'settings.show_rca':   'Mostrar salida RCA',
    'settings.rca_visible':'Salida RCA visible',
    'settings.network':    'Red',
    'settings.ip':         'IP',
    'settings.version':    'Versión',
    'settings.uptime':     'Tiempo activo',
    'settings.language':   'Idioma',
    'settings.display':    'Visualización',
    'settings.theme':      'Tema',
    'settings.theme_auto': 'Auto',
    'settings.theme_light':'Claro',
    'settings.theme_dark': 'Oscuro',
    'settings.density':    'Densidad',
    'settings.density_compact':'Compacto',
    'settings.density_default':'Predeterminado',
    'settings.density_spacious':'Espacioso',
    'settings.contrast':   'Alto contraste',
    'settings.contrast_off':'Off',
    'settings.contrast_on':'On',
    'settings.vision':     'Visión',
    'settings.vision_default':'Auto',
    'settings.vision_deutan':'Deutan',
    'settings.vision_protan':'Protan',
    'settings.vision_tritan':'Tritan',
    'settings.vision_achroma':'Achroma',
    'settings.lang_auto':  'Auto',
    'settings.about':      'Acerca de',

    'rca.label':           'RCA local',
    'common.search':       'Buscando…',
    'common.no_networks':  'No se encontraron redes',
    'common.scan_running': 'Escaneo en curso…',
    'common.back':         '← Volver',
  },
};

var LOCALE = (function () {
  var stored = (function () {
    try { return localStorage.getItem('opentrntbl-lang'); } catch (e) { return null; }
  })();
  if (stored && I18N[stored]) return stored;
  var browserLang = (navigator.language || navigator.userLanguage || 'fr').slice(0, 2).toLowerCase();
  return I18N[browserLang] ? browserLang : 'fr';
})();

function t(key) {
  return (I18N[LOCALE] && I18N[LOCALE][key]) || (I18N.fr && I18N.fr[key]) || key;
}

function setLang(lang) {
  if (!I18N[lang]) return;
  LOCALE = lang;
  try { localStorage.setItem('opentrntbl-lang', lang); } catch (e) {}
  // Re-translate everything tagged with data-i18n on the page
  document.querySelectorAll('[data-i18n]').forEach(function (el) {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
    var pairs = el.getAttribute('data-i18n-attr').split(';');
    pairs.forEach(function (pair) {
      var parts = pair.split(':');
      if (parts.length === 2) el.setAttribute(parts[0].trim(), t(parts[1].trim()));
    });
  });
  document.documentElement.lang = lang;
  // Re-render dynamic JS-built labels (Sonos status, button states, etc.)
  if (typeof refreshDynamicLabels === 'function') refreshDynamicLabels();
}

// On DOM ready: set <html lang>, hydrate static [data-i18n] elements
function hydrateI18n() {
  document.documentElement.lang = LOCALE;
  document.querySelectorAll('[data-i18n]').forEach(function (el) {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
    var pairs = el.getAttribute('data-i18n-attr').split(';');
    pairs.forEach(function (pair) {
      var parts = pair.split(':');
      if (parts.length === 2) el.setAttribute(parts[0].trim(), t(parts[1].trim()));
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', hydrateI18n);
} else {
  hydrateI18n();
}
