import api from './src/api/axios.js';
api.post('/api/extract-symptoms', { text: "I have headache" })
  .then(res => console.log("SUCCESS:", res.data))
  .catch(err => {
    console.error("ERROR:");
    if (err.response) {
      console.error("Status:", err.response.status);
      console.error("Data:", err.response.data);
    } else {
      console.error(err.message);
    }
  });
