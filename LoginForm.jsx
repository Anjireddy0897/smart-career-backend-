import React, { useState } from "react";

export default function LoginForm({ apiBaseUrl = "http://127.0.0.1:5001", onSuccess, onNavigateToRegister }) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: "",
      }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setErrors({});

    try {
      const loginPayload = {
        email: formData.email,
        password: formData.password,
      };

      const loginResponse = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loginPayload),
      });

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        if (loginData.errors) {
          setErrors(loginData.errors);
        }
        throw new Error(loginData.message || "Failed to login.");
      }

      // Success!
      if (onSuccess) {
        onSuccess(loginData.user);
      } else {
        alert(`Welcome back, ${loginData.user.full_name}!`);
      }

      setFormData({
        email: "",
        password: "",
      });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "0 auto", padding: 24 }}>
      <h2>Sign In</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>Welcome back to your career planning</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        {/* Email */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Email ✉️
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            placeholder="Enter your email"
            required
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.email ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.email && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.email}</span>}
        </div>

        {/* Password */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Password 🔒
          </label>
          <div style={{ position: "relative", display: "flex" }}>
            <input
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={(e) => handleChange("password", e.target.value)}
              placeholder="Enter your password"
              required
              style={{
                flex: 1,
                padding: "12px 14px",
                paddingRight: 44,
                borderRadius: 10,
                border: errors.password ? "2px solid #dc2626" : "1px solid #cbd5e1",
                fontSize: 14,
                fontFamily: "inherit",
              }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: 12,
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: 18,
              }}
            >
              👁️
            </button>
          </div>
          {errors.password && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.password}</span>}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "14px 18px",
            borderRadius: 12,
            border: "none",
            background: loading ? "#9ca3af" : "#2563eb",
            color: "white",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: 8,
            fontSize: 16,
          }}
        >
          {loading ? "Signing In..." : "Sign In"}
        </button>

        {/* Sign Up Link */}
        <p style={{ textAlign: "center", marginTop: 12, color: "#666" }}>
          Don't have an account?{" "}
          <button
            type="button"
            onClick={onNavigateToRegister}
            style={{
              background: "none",
              border: "none",
              color: "#2563eb",
              cursor: "pointer",
              fontWeight: 600,
              textDecoration: "underline",
            }}
          >
            Create Account
          </button>
        </p>
      </form>

      {/* Error Message */}
      {error && (
        <div style={{ marginTop: 20, padding: 16, borderRadius: 12, background: "#fee2e2", border: "1px solid #fca5a5" }}>
          <strong style={{ color: "#b91c1c" }}>Error:</strong>
          <p style={{ color: "#b91c1c", margin: "4px 0 0 0" }}>{error}</p>
        </div>
      )}
    </div>
  );
}
