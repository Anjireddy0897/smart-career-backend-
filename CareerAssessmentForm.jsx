import React, { useState } from "react";

const OPTION_LABELS = [
  { value: "1", label: "1 - Strongly Disagree" },
  { value: "2", label: "2 - Disagree" },
  { value: "3", label: "3 - Neutral" },
  { value: "4", label: "4 - Agree" },
  { value: "5", label: "5 - Strongly Agree" },
];

const QUESTIONS = [
  {
    key: "q1",
    label: "Q1. I enjoy solving logical problems, analyzing information, and finding solutions to challenging situations.",
  },
  {
    key: "q2",
    label: "Q2. I like helping people, understanding their needs, and making a positive impact on their lives.",
  },
  {
    key: "q3",
    label: "Q3. I enjoy leading teams, organizing activities, and making important decisions.",
  },
  {
    key: "q4",
    label: "Q4. I am interested in understanding laws, rules, policies, and how society is governed.",
  },
  {
    key: "q5",
    label: "Q5. I enjoy expressing my ideas through creativity, design, art, or visual storytelling.",
  },
  {
    key: "q6",
    label: "Q6. I enjoy creating content, sharing ideas, and engaging with audiences through digital platforms.",
  },
  {
    key: "q7",
    label: "Q7. I am passionate about performing arts such as music, dance, acting, or public performances.",
  },
  {
    key: "q8",
    label: "Q8. I enjoy strategic thinking, competition, gaming, and exploring new technologies or innovations.",
  },
  {
    key: "q9",
    label: "Q9. I am interested in working with nature, agriculture, transportation systems, or large-scale operations.",
  },
  {
    key: "q10",
    label: "Q10. I prefer creating my own opportunities, taking initiative, and building something independently.",
  },
];

const initialAnswers = QUESTIONS.reduce((accumulator, question) => {
  accumulator[question.key] = "";
  return accumulator;
}, {});

export default function CareerAssessmentForm({ userId, email, apiBaseUrl = "http://127.0.0.1:5001", onSubmitted }) {
  const [answers, setAnswers] = useState(initialAnswers);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const visibleRecommendedCareers = result?.recommendedCareers || result?.recommendations || [];
  const visibleTopDomains = result?.topDomains || [];
  const simpleRecommendations = visibleRecommendedCareers.slice(0, 3);

  const handleChange = (questionKey, value) => {
    setAnswers((current) => ({
      ...current,
      [questionKey]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      if (!userId && !email) {
        throw new Error("Pass either userId or email to submit the assessment.");
      }

      const payload = {
        ...answers,
      };

      if (userId) {
        payload.user_id = userId;
      } else {
        payload.email = email;
      }

      const response = await fetch(`${apiBaseUrl}/api/career-recommendation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to submit assessment.");
      }

      setResult(data);
      sessionStorage.setItem("latestCareerRecommendation", JSON.stringify(data));
      if (typeof onSubmitted === "function") {
        onSubmitted(data);
      }
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: 24 }}>
      <h2>Career Assessment</h2>
      <p>Fill all 10 questions and submit to get a dynamic career recommendation path.</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        {QUESTIONS.map((question) => (
          <label key={question.key} style={{ display: "grid", gap: 8 }}>
            <span style={{ fontWeight: 600 }}>{question.label}</span>
            <select
              value={answers[question.key]}
              onChange={(event) => handleChange(question.key, event.target.value)}
              required
              style={{ padding: "12px 14px", borderRadius: 10, border: "1px solid #cbd5e1" }}
            >
              <option value="">Select one</option>
              {OPTION_LABELS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ))}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "14px 18px",
            borderRadius: 12,
            border: "none",
            background: "#2563eb",
            color: "white",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Submitting..." : "Submit Assessment"}
        </button>
      </form>

      {error ? (
        <div style={{ marginTop: 20, color: "#b91c1c" }}>
          <strong>Error:</strong> {error}
        </div>
      ) : null}

      {result ? (
        <div style={{ marginTop: 28, padding: 20, borderRadius: 16, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
          <h3 style={{ marginTop: 0 }}>Simple assessment result</h3>

          <div style={{ marginBottom: 18, padding: 14, borderRadius: 12, background: "#fff", border: "1px solid #e2e8f0" }}>
            <div style={{ fontSize: 14, color: "#64748b", marginBottom: 6 }}>Top Domains Identified</div>
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {visibleTopDomains.slice(0, 3).map((domain) => (
                <li key={domain} style={{ marginBottom: 6, fontWeight: 700 }}>
                  {domain}
                </li>
              ))}
            </ol>
          </div>

          <div style={{ display: "grid", gap: 10 }}>
            <strong>Top matches</strong>
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {simpleRecommendations.map((career, index) => (
                <li key={`${career.career}-${index}`} style={{ marginBottom: 8 }}>
                  <div style={{ fontWeight: 600 }}>{career.career}</div>
                  <div style={{ color: "#475569" }}>{career.description}</div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      ) : null}
    </div>
  );
}
