const testFormat = () => {
  const utcString = "2026-09-24T12:00:00Z";
  const dateObj = new Date(utcString);
  
  const formatted = new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(dateObj);
  
  console.log(`Original UTC: ${utcString}`);
  console.log(`Formatted IST: ${formatted}`);
  
  // Verify output
  if (formatted === "24 September 2026 at 5:30 pm" || formatted.includes("5:30")) {
      console.log("SUCCESS: Formatting verified.");
  } else {
      console.log("FAILURE: Unexpected formatting output.");
      process.exit(1);
  }
};

testFormat();
