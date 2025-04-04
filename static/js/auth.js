// Login
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  
    const data = await res.json();
    document.getElementById("loginMessage").textContent = data.message || data.error;
  
    if (res.ok) location.href = "/dashboard";
  });
  
  // Register
  document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("regUsername").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;
    const role = document.getElementById("regRole").value;
  
    const res = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, role }),
    });
  
    const data = await res.json();
    document.getElementById("registerMessage").textContent = data.message || data.error;
  
    if (res.ok) location.href = "/login";
  });
  