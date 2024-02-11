const data = {
  namespaced: true,
  state: () => ({
    sizePresetDictionary: [
      {
        label: "512 * 512",
        value: [512, 512],
      },
      {
        label: "512 * 768",
        value: [512, 768],
      },
      {
        label: "1024 * 1024",
        value: [1024, 1024],
      },
      {
        label: "1024 * 768",
        value: [1024, 768],
      },
      {
        label: "1280 * 720",
        value: [1280, 720],
      },
      {
        label: "1600 * 1000",
        value: [1600, 1000],
      },
      {
        label: "1600 * 1200",
        value: [1600, 1200],
      },
      {
        label: "1920 * 1080",
        value: [1920, 1080],
      },
    ],
    
    samplerDictionary: [{
      label: "DPM++ 2M",
      value: 'DPM++ 2M',
    }, {
      label: "DPM++ 2M Karras",
      value: 'DPM++ 2M Karras',
    }, {
      label: "DPM++ 2M SDE",
      value: 'DPM++ 2M SDE',
    }, {
      label: "DPM++ 2M SDE Karras",
      value: 'DPM++ 2M SDE Karras',
    }, {
      label: "DPM++ 2S a",
      value: 'DPM++ 2S a',
    }, {
      label: "DPM++ 2S a Karras",
      value: 'DPM++ 2S a Karras',
    }, {
      label: "DPM++ SDE",
      value: 'DPM++ SDE',
    }, {
      label: "DPM++ SDE Karras",
      value: 'DPM++ SDE Karras',
    }, {
      label: "DPM2",
      value: 'DPM2',
    }, {
      label: "DPM2 Karras",
      value: 'DPM2 Karras',
    }, {
      label: "DPM2 a",
      value: 'DPM2 a',
    }, {
      label: "DPM2 a Karras",
      value: 'DPM2 a Karras',
    }, {
      label: "DPM adaptive",
      value: 'DPM adaptive',
    }, {
      label: "DPM fast",
      value: 'DPM fast',
    }, {
      label: "Euler",
      value: 'Euler',
    }, {
      label: "Euler a",
      value: 'Euler a',
    }, {
      label: "Heun",
      value: 'Heun',
    }, {
      label: "LMS",
      value: 'LMS',
    }, {
      label: "LMS Karras",
      value: 'LMS Karras',
    }]
  }),
  mutations: {},
  actions: {},
  getters: {},
};

export default data;
