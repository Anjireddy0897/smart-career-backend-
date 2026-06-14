import React, { useState } from "react";
import RegisterForm from "./RegisterForm.jsx";
import LoginForm from "./LoginForm.jsx";
import PersonalDetailsForm from "./PersonalDetailsForm.jsx";
import EducationDetailsForm from "./EducationDetailsForm.jsx";
import CareerAssessmentForm from "./CareerAssessmentForm.jsx";
import ChatAssistant from "./ChatAssistant.jsx";

const API_BASE_URL = "http://127.0.0.1:5001";

function getPageFromPathname() {
  if (window.location.pathname.startsWith("/recommendation")) {
    return "recommendation";
  }
  return "home";
}

function RecommendationResultPage({ onGoHome }) {
  let savedResult = null;

  try {
    const rawValue = sessionStorage.getItem("latestCareerRecommendation");
    savedResult = rawValue ? JSON.parse(rawValue) : null;
  } catch {
    savedResult = null;
  }

  const topDomains = savedResult?.topDomains || [];
  const recommendedCareers = savedResult?.recommendedCareers || savedResult?.recommendations || [];
  const simpleRecommendations = recommendedCareers.slice(0, 3);

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc" }}>
      <header style={{ background: "linear-gradient(90deg, #4f46e5, #9333ea)", color: "white", padding: "14px 20px", fontWeight: 700, fontSize: 20 }}>
        Career Recommendations
      </header>
      <main style={{ maxWidth: 760, margin: "0 auto", padding: "32px 20px 56px" }}>
        <div style={{ marginBottom: 16, color: "#334155", textAlign: "center" }}>Simple assessment result</div>

        <section style={{ marginBottom: 18, padding: 16, borderRadius: 14, background: "white", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: 14, color: "#64748b", marginBottom: 6 }}>Top Domains Identified</div>
          <ol style={{ margin: 0, paddingLeft: 22 }}>
            {topDomains.slice(0, 3).map((domain) => (
              <li key={domain} style={{ marginBottom: 6, fontWeight: 700 }}>{domain}</li>
            ))}
          </ol>
        </section>

        <section style={{ marginBottom: 24 }}>
          <h4 style={{ margin: "0 0 10px" }}>Top matches</h4>
          <ol style={{ margin: 0, paddingLeft: 22 }}>
            {simpleRecommendations.map((career, index) => (
              <li key={`${career.career}-${index}`} style={{ marginBottom: 10 }}>
                <div style={{ fontWeight: 600 }}>{career.career}</div>
                <div style={{ color: "#475569" }}>{career.description}</div>
              </li>
            ))}
          </ol>
        </section>

        <button
          onClick={onGoHome}
          style={{
            display: "block",
            margin: "0 auto",
            padding: "12px 22px",
            borderRadius: 999,
            border: "none",
            background: "linear-gradient(90deg, #4f46e5, #d946ef)",
            color: "white",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Return to Home
        </button>
      </main>
    </div>
  );
}

export default function App() {
  const [currentPage, setCurrentPage] = useState(getPageFromPathname()); // home, register, login, dashboard, recommendation
  const [currentUser, setCurrentUser] = useState(null);
  const [currentStep, setCurrentStep] = useState(1); // 1: personal, 2: education, 3: assessment

  React.useEffect(() => {
    const syncPage = () => setCurrentPage(getPageFromPathname());
    window.addEventListener("popstate", syncPage);
    return () => window.removeEventListener("popstate", syncPage);
  }, []);

  const handleRegisterSuccess = (user) => {
    setCurrentUser(user);
    setCurrentPage("dashboard");
    setCurrentStep(1);
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setCurrentPage("dashboard");
    setCurrentStep(1);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentPage("home");
    setCurrentStep(1);
    window.history.pushState({}, "", "/");
  };

  const handleAssessmentSubmitted = (result) => {
    sessionStorage.setItem("latestCareerRecommendation", JSON.stringify(result));
    window.history.pushState({}, "", "/recommendation");
    setCurrentPage("recommendation");
  };

  const handleNextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      alert("You've completed all steps! Career assessment submitted.");
      handleLogout();
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f1f5f9" }}>
      {/* Header */}
      <header style={{ background: "#2563eb", color: "white", padding: "20px", textAlign: "center", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        <h1 style={{ margin: 0 }}>🚀 Smart Career Planning</h1>
        <p style={{ margin: "8px 0 0 0", fontSize: 14 }}>Your journey to the perfect career starts here</p>
        {currentUser && (
          <div style={{ marginTop: 12, fontSize: 14 }}>
            <span>Welcome, <strong>{currentUser.full_name}</strong>!</span>
            <button
              onClick={handleLogout}
              style={{
                marginLeft: 16,
                background: "rgba(255,255,255,0.2)",
                border: "1px solid white",
                color: "white",
                padding: "6px 12px",
                borderRadius: 6,
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              Sign Out
            </button>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "40px 20px" }}>
        {/* Home Page */}
        {currentPage === "home" && !currentUser && (
          <div style={{ display: "grid", gap: 24 }}>
            <div style={{ textAlign: "center" }}>
              <h2 style={{ fontSize: 28, marginBottom: 24 }}>Welcome to Smart Career Planning</h2>
              <p style={{ fontSize: 16, color: "#666", marginBottom: 32 }}>
                Take our comprehensive career assessment and get personalized recommendations based on your interests.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, maxWidth: 600, margin: "0 auto" }}>
                <button
                  onClick={() => setCurrentPage("register")}
                  style={{
                    padding: "16px 24px",
                    borderRadius: 12,
                    border: "none",
                    background: "#2563eb",
                    color: "white",
                    fontWeight: 700,
                    cursor: "pointer",
                    fontSize: 16,
                  }}
                >
                  Create Account
                </button>
                <button
                  onClick={() => setCurrentPage("login")}
                  style={{
                    padding: "16px 24px",
                    borderRadius: 12,
                    border: "2px solid #2563eb",
                    background: "white",
                    color: "#2563eb",
                    fontWeight: 700,
                    cursor: "pointer",
                    fontSize: 16,
                  }}
                >
                  Sign In
                </button>
              </div>
            </div>

            <ChatAssistant apiBaseUrl={API_BASE_URL} />
          </div>
        )}

        {/* Register Page */}
        {currentPage === "register" && !currentUser && (
          <RegisterForm
            apiBaseUrl={API_BASE_URL}
            onSuccess={handleRegisterSuccess}
            onNavigateToLogin={() => setCurrentPage("login")}
          />
        )}

        {/* Login Page */}
        {currentPage === "login" && !currentUser && (
          <LoginForm
            apiBaseUrl={API_BASE_URL}
            onSuccess={handleLoginSuccess}
            onNavigateToRegister={() => setCurrentPage("register")}
          />
        )}

        {/* Dashboard - Multi-step Form */}
        {currentPage === "dashboard" && currentUser && (
          <div>
            {/* Progress Indicator */}
            <div style={{ marginBottom: 32, textAlign: "center" }}>
              <div style={{ display: "flex", justifyContent: "center", gap: 16, marginBottom: 16 }}>
                {[1, 2, 3].map((step) => (
                  <div
                    key={step}
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: "50%",
                      background: step <= currentStep ? "#2563eb" : "#cbd5e1",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 700,
                      transition: "all 0.3s ease",
                    }}
                  >
                    {step < currentStep ? "✓" : step}
                  </div>
                ))}
              </div>
              <p style={{ color: "#666", margin: 0 }}>
                {currentStep === 1 && "Step 1: Personal Details"}
                {currentStep === 2 && "Step 2: Education Details"}
                {currentStep === 3 && "Step 3: Career Assessment"}
              </p>
            </div>

            {/* Step 1: Personal Details */}
            {currentStep === 1 && (
              <>
                <PersonalDetailsForm
                  userId={currentUser.id}
                  apiBaseUrl={API_BASE_URL}
                />
                <div style={{ textAlign: "center", marginTop: 24 }}>
                  <button
                    onClick={handleNextStep}
                    style={{
                      padding: "12px 32px",
                      borderRadius: 12,
                      border: "none",
                      background: "#2563eb",
                      color: "white",
                      fontWeight: 700,
                      cursor: "pointer",
                      fontSize: 16,
                    }}
                  >
                    Next Step →
                  </button>
                </div>
              </>
            )}

            {/* Step 2: Education Details */}
            {currentStep === 2 && (
              <>
                <EducationDetailsForm
                  userId={currentUser.id}
                  apiBaseUrl={API_BASE_URL}
                />
                <div style={{ textAlign: "center", marginTop: 24, display: "flex", gap: 12, justifyContent: "center" }}>
                  <button
                    onClick={() => setCurrentStep(1)}
                    style={{
                      padding: "12px 32px",
                      borderRadius: 12,
                      border: "2px solid #2563eb",
                      background: "white",
                      color: "#2563eb",
                      fontWeight: 700,
                      cursor: "pointer",
                      fontSize: 16,
                    }}
                  >
                    ← Back
                  </button>
                  <button
                    onClick={handleNextStep}
                    style={{
                      padding: "12px 32px",
                      borderRadius: 12,
                      border: "none",
                      background: "#2563eb",
                      color: "white",
                      fontWeight: 700,
                      cursor: "pointer",
                      fontSize: 16,
                    }}
                  >
                    Next Step →
                  </button>
                </div>
              </>
            )}

            {/* Step 3: Career Assessment */}
            {currentStep === 3 && (
              <>
                <CareerAssessmentForm
                  userId={currentUser.id}
                  apiBaseUrl={API_BASE_URL}
                  onSubmitted={handleAssessmentSubmitted}
                />
                <div style={{ textAlign: "center", marginTop: 24 }}>
                  <button
                    onClick={() => setCurrentStep(2)}
                    style={{
                      padding: "12px 32px",
                      borderRadius: 12,
                      border: "2px solid #2563eb",
                      background: "white",
                      color: "#2563eb",
                      fontWeight: 700,
                      cursor: "pointer",
                      fontSize: 16,
                    }}
                  >
                    ← Back
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {currentPage === "recommendation" && (
          <RecommendationResultPage
            onGoHome={() => {
              window.history.pushState({}, "", "/");
              setCurrentPage("home");
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{ background: "#1e293b", color: "white", padding: "24px", textAlign: "center", marginTop: 64 }}>
        <p style={{ margin: 0, fontSize: 14 }}>© 2026 Smart Career Planning. All rights reserved.</p>
      </footer>
    </div>
  );
}
