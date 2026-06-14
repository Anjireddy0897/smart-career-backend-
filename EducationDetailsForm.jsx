import React, { useState } from "react";

const EDUCATION_LEVELS = [
  { value: "10th", label: "10th Grade" },
  { value: "12th", label: "12th Grade" },
  { value: "diploma", label: "Diploma" },
  { value: "bachelors", label: "Bachelor's Degree" },
  { value: "masters", label: "Master's Degree" },
  { value: "phd", label: "PhD" },
  { value: "other", label: "Other" },
];

const STREAMS = [
  { value: "science", label: "Science" },
  { value: "commerce", label: "Commerce" },
  { value: "arts", label: "Arts" },
  { value: "engineering", label: "Engineering" },
  { value: "medical", label: "Medical" },
  { value: "business", label: "Business" },
  { value: "other", label: "Other" },
];

export default function EducationDetailsForm({ userId, email, apiBaseUrl = "http://127.0.0.1:5001" }) {
  const [formData, setFormData] = useState({
    current_education_level: "",
    stream: "",
    school_college_name: "",
    average_percentage_gpa: "",
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
        throw new Error("Pass either userId or email to submit education details.");
      }

      const payload = {
        ...formData,
      };

      if (userId) {
        payload.user_id = userId;
      } else {
        payload.email = email;
      }

      const response = await fetch(`${apiBaseUrl}/api/education-details`, {
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
        throw new Error(data.message || "Failed to save education details.");
      }

      setSuccess("Education details saved successfully!");
      setFormData({
        current_education_level: "",
        stream: "",
        school_college_name: "",
        average_percentage_gpa: "",
      });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h2>Education Details 🎓</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>Step 2 of 4</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        {/* Current Education Level */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Current Education Level
          </label>
          <select
            value={formData.current_education_level}
            onChange={(e) => handleChange("current_education_level", e.target.value)}
            required
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.current_education_level ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          >
            <option value="">Select education level</option>
            {EDUCATION_LEVELS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.current_education_level && (
            <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.current_education_level}</span>
          )}
        </div>

        {/* Stream */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Stream (Optional)
          </label>
          <select
            value={formData.stream}
            onChange={(e) => handleChange("stream", e.target.value)}
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.stream ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          >
            <option value="">Select stream</option>
            {STREAMS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.stream && <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.stream}</span>}
        </div>

        {/* School/College Name */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            School/College Name
          </label>
          <input
            type="text"
            value={formData.school_college_name}
            onChange={(e) => handleChange("school_college_name", e.target.value)}
            placeholder="Enter your school or college name"
            required
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.school_college_name ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.school_college_name && (
            <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.school_college_name}</span>
          )}
        </div>

        {/* Average Percentage/GPA */}
        <div style={{ display: "grid", gap: 6 }}>
          <label style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            Average Percentage/GPA
          </label>
          <input
            type="text"
            value={formData.average_percentage_gpa}
            onChange={(e) => handleChange("average_percentage_gpa", e.target.value)}
            placeholder="e.g., 85% or 3.8 GPA"
            required
            style={{
              padding: "12px 14px",
              borderRadius: 10,
              border: errors.average_percentage_gpa ? "2px solid #dc2626" : "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "inherit",
            }}
          />
          {errors.average_percentage_gpa && (
            <span style={{ color: "#dc2626", fontSize: 12 }}>{errors.average_percentage_gpa}</span>
          )}
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
          {loading ? "Saving..." : "Save Education Details"}
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
