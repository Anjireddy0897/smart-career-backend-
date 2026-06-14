import React, { useState } from "react";

const GENDER_OPTIONS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "other", label: "Other" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

export default function RegisterForm({ apiBaseUrl = "http://127.0.0.1:5001", onSuccess, onNavigateToLogin }) {
  const [formData, setFormData] = useState({
    full_name: "",
    gender: "",
    phone_number: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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
      // Step 1: Register user (full_name, email, password)
      const registerPayload = {
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirm_password,
      };

      const registerResponse = await fetch(`${apiBaseUrl}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(registerPayload),
      });

      const registerData = await registerResponse.json();

      if (!registerResponse.ok) {
        if (registerData.errors) {
          setErrors(registerData.errors);
        }
        throw new Error(registerData.message || "Failed to create account.");
      }

      const userId = registerData.user.id;

      // Step 2: Save personal details (gender, phone_number) if provided
      if (formData.gender || formData.phone_number) {
        const personalDetailsPayload = {
          user_id: userId,
          gender: formData.gender,
          phone_number: formData.phone_number,
          date_of_birth: "", // Optional, can be empty
          city: "", // Optional, can be empty
        };

        const personalResponse = await fetch(`${apiBaseUrl}/api/personal-details`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(personalDetailsPayload),
        });

        const personalData = await personalResponse.json();
        
        // Log but don't fail if personal details save fails
        if (!personalResponse.ok) {
          console.warn("Personal details save warning:", personalData.message);
        }
      }

      // Success!
      if (onSuccess) {
        onSuccess(registerData.user);
      } else {
        alert(`Account created successfully! Welcome, ${registerData.user.full_name}`);
      }

      setFormData({
        full_name: "",
        gender: "",
        phone_number: "",
        email: "",
        password: "",
        confirm_password: "",
      });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "0 auto", padding: 24 }}>
      <h2>Create Account</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>Start your career planning journey</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        {/* Full Name */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Full Name 👤
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => handleChange("full_name", e.target.value)}
            placeholder="Enter your full name"
            required
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.full_name ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.full_name && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.full_name}</span>}
        </div>

        {/* Gender */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Gender ⚧
          </label>
          <select
            value={formData.gender}
            onChange={(e) => handleChange("gender", e.target.value)}
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.gender ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          >
            <option value="">Select your gender</option>
            {GENDER_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.gender && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.gender}</span>}
        </div>

        {/* Phone Number */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Phone Number 📞
          </label>
          <input
            type="tel"
            value={formData.phone_number}
            onChange={(e) => handleChange("phone_number", e.target.value)}
            placeholder="Enter phone number (7-15 digits)"
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.phone_number ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.phone_number && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.phone_number}</span>}
        </div>

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
              placeholder="Min 6 characters"
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

        {/* Confirm Password */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Confirm Password 🔒
          </label>
          <div style={{ position: "relative", display: "flex" }}>
            <input
              type={showConfirmPassword ? "text" : "password"}
              value={formData.confirm_password}
              onChange={(e) => handleChange("confirm_password", e.target.value)}
              placeholder="Confirm your password"
              required
              style={{
                flex: 1,
                padding: "12px 14px",
                paddingRight: 44,
                borderRadius: 10,
                border: errors.confirm_password ? "2px solid #dc2626" : "1px solid #cbd5e1",
                fontSize: 14,
                fontFamily: "inherit",
              }}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
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
          {errors.confirm_password && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.confirm_password}</span>}
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
          {loading ? "Creating Account..." : "Create Account"}
        </button>

        {/* Sign In Link */}
        <p style={{ textAlign: "center", marginTop: 12, color: "#666" }}>
          Already have an account?{" "}
          <button
            type="button"
            onClick={onNavigateToLogin}
            style={{
              background: "none",
              border: "none",
              color: "#2563eb",
              cursor: "pointer",
              fontWeight: 600,
              textDecoration: "underline",
            }}
          >
            Sign In
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
