import { analysisApi } from './src/api/analysisApi.js';
analysisApi.extractSymptoms('I have a headache')
  .then(console.log)
  .catch(console.error);
