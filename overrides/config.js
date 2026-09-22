window.CMH_CONFIG = {
  GAME_TITLE: 'Capture My Heart! Territory Panic',
  VERSION: '0.8.2',
  GAMEPLAY: {
    DANGER_BGM_ENABLED: false,
    DANGER_VISUAL_ENABLED: true,
    CAMERA_ZOOM: 1.50,
    MINIMAP_ENABLED: true
  },
  ADS: {
    ENABLED: false,
    PUBLISHER_ID: 'ca-pub-6414931308880829',
    TEST_MODE: false,
    FREQUENCY_HINT: '120s',
    INTERSTITIAL_AFTER_STAGES: [2, 4, 6, 8],
    MIN_SECONDS_BETWEEN_INTERSTITIALS: 120
  },
  FEEDBACK: {
    ENABLED: true,
    ENDPOINT: 'https://cvfmikycscmfjmooxhni.supabase.co/rest/v1/cmh_feedback',
    API_KEY: 'sb_publishable_AlQwZgMrOCznUo4LQePZiw_maIjWv6w',
    REQUEST_TIMEOUT_MS: 6500,
    MAX_LOCAL_QUEUE: 50
  },
  ANALYTICS: {
    ENABLED: true,
    ENDPOINT: 'https://cvfmikycscmfjmooxhni.supabase.co/rest/v1/cmh_analytics_events',
    API_KEY: 'sb_publishable_AlQwZgMrOCznUo4LQePZiw_maIjWv6w',
    REQUEST_TIMEOUT_MS: 5500,
    MAX_LOCAL_QUEUE: 200,
    GA_MEASUREMENT_ID: ''
  }
};
