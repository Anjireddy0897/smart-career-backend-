import React, { useState } from "react";

const GENDER_OPTIONS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "other", label: "Other" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

export default function PersonalDetailsForm({ userId, email, apiBaseUrl = "http://127.0.0.1:5001" }) {
  const [formData, setFormData] = useState({
    full_name: "",
    date_of_birth: "",
    gender: "",
    phone_number: "",
    city: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [errors, setErrors] = useState({});

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
    setSuccess("");
    setErrors({});

    try {
      if (!userId && !email) {
        throw new Error("Pass either userId or email to submit personal details.");
      }

      const payload = {
        ...formData,
      };

      if (userId) {
        payload.user_id = userId;
      } else {
        payload.email = email;
      }

      const response = await fetch(`${apiBaseUrl}/api/personal-details`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.errors) {
          setErrors(data.errors);
        }
        throw new Error(data.message || "Failed to save personal details.");
      }

      setSuccess("Personal details saved successfully!");
      setFormData({
        full_name: "",
        date_of_birth: "",
        gender: "",
        phone_number: "",
        city: "",
      });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h2>Personal Details 👤</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>Step 1 of 4</p>

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

        {/* Date of Birth */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Date of Birth 📅
          </label>
          <input
            type="date"
            value={formData.date_of_birth}
            onChange={(e) => handleChange("date_of_birth", e.target.value)}
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.date_of_birth ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.date_of_birth && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.date_of_birth}</span>}
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

        {/* City */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            City 📍
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => handleChange("city", e.target.value)}
            placeholder="Enter your city"
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.city ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.city && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.city}</span>}
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
          {loading ? "Saving..." : "Save Personal Details"}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div style={{ marginTop: 20, padding: 16, borderRadius: 12, background: "#fee2e2", border: "1px solid #fca5a5" }}>
          <strong style={{ color: "#b91c1c" }}>Error:</strong>
          <p style={{ color: "#b91c1c", margin: "4px 0 0 0" }}>{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div style={{ marginTop: 20, padding: 16, borderRadius: 12, background: "#dcfce7", border: "1px solid #86efac" }}>
          <strong style={{ color: "#15803d" }}>✓ Success:</strong>
          <p style={{ color: "#15803d", margin: "4px 0 0 0" }}>{success}</p>
        </div>
      )}
    </div>
  );
}
