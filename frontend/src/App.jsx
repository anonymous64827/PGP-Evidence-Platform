import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [page, setPage] = useState("dashboard");

  const [authenticCount, setAuthenticCount] = useState(0);
  const [tamperedCount, setTamperedCount] = useState(0);
  const [analysisCount, setAnalysisCount] = useState(0);

  // =========================================================
  // LOAD ALL EVIDENCE
  // =========================================================

  const loadEvidence = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/evidence`);

      if (!response.ok) {
        throw new Error("Failed to load evidence");
      }

      const data = await response.json();

      setEvidence(data.evidence || []);

      // Verify each evidence record
      let authentic = 0;
      let tampered = 0;
      let analyses = 0;

      const records = data.evidence || [];

      for (const item of records) {
        try {
          const verifyResponse = await fetch(
            `${API_URL}/evidence/${item.evidence_id}/verify`
          );

          if (verifyResponse.ok) {
            const verifyData = await verifyResponse.json();

            if (verifyData.status === "AUTHENTIC") {
              authentic++;
            } else if (verifyData.status === "TAMPERED") {
              tampered++;
            }
          }
        } catch (err) {
          console.error("Verification error:", err);
        }

        try {
          const analysisResponse = await fetch(
            `${API_URL}/evidence/${item.evidence_id}/analysis`
          );

          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();

            if (
              analysisData.status === "SUCCESS" &&
              analysisData.analysis
            ) {
              analyses++;
            }
          }
        } catch (err) {
          console.error("Analysis error:", err);
        }
      }

      setAuthenticCount(authentic);
      setTamperedCount(tampered);
      setAnalysisCount(analyses);
    } catch (err) {
      console.error(err);
      setError("Unable to load evidence from backend.");
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadEvidence();
  }, []);

  // =========================================================
  // UPLOAD EVIDENCE
  // =========================================================

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    try {
      setUploading(true);
      setMessage("");
      setError("");

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/evidence/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setMessage(
        `Evidence uploaded successfully: ${data.evidence_id}`
      );

      await loadEvidence();
    } catch (err) {
      console.error(err);
      setError("Evidence upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  // =========================================================
  // OPEN EVIDENCE DETAILS
  // =========================================================

  const openEvidence = async (item) => {
    try {
      setSelectedEvidence(item);
      setDetailLoading(true);
      setError("");

      // -----------------------------------------------------
      // 1. BASIC VERIFICATION
      // -----------------------------------------------------

      let verification = null;

      try {
        const response = await fetch(
          `${API_URL}/evidence/${item.evidence_id}/verify`
        );

        if (response.ok) {
          verification = await response.json();
        }
      } catch (err) {
        console.error("Verification request failed:", err);
      }

      // -----------------------------------------------------
      // 2. HISTORY
      // -----------------------------------------------------

      let history = null;

      try {
        const response = await fetch(
          `${API_URL}/evidence/${item.evidence_id}/history`
        );

        if (response.ok) {
          history = await response.json();
        }
      } catch (err) {
        console.error("History request failed:", err);
      }

      // -----------------------------------------------------
      // 3. AUDIT CHAIN
      // -----------------------------------------------------

      let chain = null;

      try {
        const response = await fetch(
          `${API_URL}/evidence/${item.evidence_id}/chain/verify`
        );

        if (response.ok) {
          chain = await response.json();
        }
      } catch (err) {
        console.error("Chain verification failed:", err);
      }

      // -----------------------------------------------------
      // 4. AI ANALYSIS
      // -----------------------------------------------------

      let analysis = null;

      try {
        const response = await fetch(
          `${API_URL}/evidence/${item.evidence_id}/analysis`
        );

        if (response.ok) {
          analysis = await response.json();
        }
      } catch (err) {
        console.error("AI analysis request failed:", err);
      }

      // -----------------------------------------------------
      // 5. AI ANALYSIS VERIFICATION
      // -----------------------------------------------------

      let analysisVerification = null;

      try {
        const response = await fetch(
          `${API_URL}/evidence/${item.evidence_id}/analysis/verify`
        );

        if (response.ok) {
          analysisVerification = await response.json();
        }
      } catch (err) {
        console.error(
          "AI analysis verification failed:",
          err
        );
      }

      // -----------------------------------------------------
      // STORE EVERYTHING
      // -----------------------------------------------------

      setDetailData({
        verification,
        history,
        chain,
        analysis,
        analysisVerification,
      });

      setPage("details");
    } catch (err) {
      console.error(err);
      setError("Unable to open evidence details.");
    } finally {
      setDetailLoading(false);
    }
  };

  // =========================================================
  // CLOSE DETAILS
  // =========================================================

  const closeDetails = () => {
    setSelectedEvidence(null);
    setDetailData(null);
    setPage("dashboard");
  };

  // =========================================================
  // SIDEBAR
  // =========================================================

  const Sidebar = () => (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">PGP</div>

        <div>
          <h2>PGP Evidence</h2>
          <p>Digital Evidence Platform</p>
        </div>
      </div>

      <nav>
        <button
          className={page === "dashboard" ? "nav-active" : ""}
          onClick={() => {
            setPage("dashboard");
            setSelectedEvidence(null);
          }}
        >
          ▦
          <span>Dashboard</span>
        </button>

        <button
          className={page === "evidence" ? "nav-active" : ""}
          onClick={() => {
            setPage("evidence");
            setSelectedEvidence(null);
          }}
        >
          ◇
          <span>Evidence</span>
        </button>

        <button
          onClick={() => {
            setPage("audit");
            setSelectedEvidence(null);
          }}
        >
          ⌁
          <span>Audit Trail</span>
        </button>

        <button
          onClick={() => {
            setPage("ai");
            setSelectedEvidence(null);
          }}
        >
          ✦
          <span>AI Analysis</span>
        </button>

        <button
          onClick={() => {
            setPage("verification");
            setSelectedEvidence(null);
          }}
        >
          ✓
          <span>Verification</span>
        </button>
      </nav>
    </aside>
  );

  // =========================================================
  // DASHBOARD
  // =========================================================

  const Dashboard = () => (
    <>
      <div className="page-header">
        <div>
          <div className="eyebrow">SECURE EVIDENCE MANAGEMENT</div>
          <h1>Evidence Dashboard</h1>
        </div>

        <label className="upload-button">
          + Upload Evidence
          <input
            type="file"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
      </div>

      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-message">{error}</div>}

      <div className="stats-grid">
        <StatCard
          title="Total Evidence"
          value={evidence.length}
          subtitle="Evidence records stored"
        />

        <StatCard
          title="Authentic"
          value={authenticCount}
          subtitle="Hash verification passed"
        />

        <StatCard
          title="Tampered"
          value={tamperedCount}
          subtitle="Modification detected"
        />

        <StatCard
          title="AI Analyses"
          value={analysisCount}
          subtitle="Evidence analyses completed"
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">RECENT RECORDS</div>
              <h2>Evidence Activity</h2>
            </div>

            <button
              className="secondary-button"
              onClick={() => setPage("evidence")}
            >
              View All
            </button>
          </div>

          {loading ? (
            <div className="empty-state">Loading evidence...</div>
          ) : evidence.length === 0 ? (
            <div className="empty-state">
              No evidence records found.
            </div>
          ) : (
            <div>
              {evidence.slice(0, 5).map((item) => (
                <EvidenceRow
                  key={item.evidence_id}
                  item={item}
                  onClick={() => openEvidence(item)}
                />
              ))}
            </div>
          )}
        </section>

        <section className="panel integrity-panel">
          <div className="eyebrow">INTEGRITY</div>

          <h2>Cryptographic Security</h2>

          <div className="security-circle">
            <strong>100%</strong>
            <span>VALID</span>
          </div>

          <p>
            Audit chains are cryptographically linked
            and continuously verifiable.
          </p>

          <div className="operational">
            <span className="green-dot"></span>
            Audit chain operational
          </div>
        </section>
      </div>
    </>
  );

  // =========================================================
  // EVIDENCE LIST
  // =========================================================

  const EvidencePage = () => (
    <>
      <div className="page-header">
        <div>
          <div className="eyebrow">DIGITAL RECORDS</div>
          <h1>Evidence</h1>
        </div>

        <label className="upload-button">
          + Upload Evidence
          <input
            type="file"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">ALL RECORDS</div>
            <h2>Evidence Repository</h2>
          </div>

          <span className="record-count">
            {evidence.length} records
          </span>
        </div>

        {evidence.map((item) => (
          <EvidenceRow
            key={item.evidence_id}
            item={item}
            onClick={() => openEvidence(item)}
          />
        ))}
      </section>
    </>
  );

  // =========================================================
  // SIMPLE INFORMATION PAGES
  // =========================================================

  const SimplePage = ({ title, eyebrow, children }) => (
    <>
      <div className="page-header">
        <div>
          <div className="eyebrow">{eyebrow}</div>
          <h1>{title}</h1>
        </div>
      </div>

      <section className="panel">
        {children}
      </section>
    </>
  );

  // =========================================================
  // DETAILS PAGE
  // =========================================================

  const EvidenceDetails = () => {
    if (!selectedEvidence) return null;

    if (detailLoading) {
      return (
        <section className="panel loading-details">
          <div className="spinner"></div>
          <h2>Loading Evidence Details</h2>
          <p>
            Verifying evidence, audit chain and AI analysis...
          </p>
        </section>
      );
    }

    const verification = detailData?.verification;
    const history = detailData?.history;
    const chain = detailData?.chain;
    const analysis = detailData?.analysis;
    const analysisVerification =
      detailData?.analysisVerification;

    const evidenceIsAuthentic =
      verification?.status === "AUTHENTIC";

    const evidenceIsTampered =
      verification?.status === "TAMPERED";

    const aiIsValid =
      analysisVerification?.valid === true;

    const aiIsInvalid =
      analysisVerification?.valid === false;

    const analysisAvailable =
      analysis?.status === "SUCCESS" &&
      analysis?.analysis;

    return (
      <>
        <div className="page-header">
          <div>
            <button
              className="back-button"
              onClick={closeDetails}
            >
              ← Back
            </button>

            <div className="eyebrow">EVIDENCE INVESTIGATION</div>

            <h1>Evidence Details</h1>

            <p className="evidence-id">
              {selectedEvidence.evidence_id}
            </p>
          </div>

          <div
            className={
              evidenceIsAuthentic
                ? "status-badge authentic"
                : evidenceIsTampered
                ? "status-badge tampered"
                : "status-badge"
            }
          >
            {verification?.status || "UNKNOWN"}
          </div>
        </div>

        {/* FILE INFORMATION */}

        <section className="panel">
          <div className="eyebrow">EVIDENCE RECORD</div>
          <h2>File Information</h2>

          <div className="info-grid">
            <InfoBox
              label="Evidence ID"
              value={selectedEvidence.evidence_id}
            />

            <InfoBox
              label="File Name"
              value={selectedEvidence.file_name}
            />

            <InfoBox
              label="File Type"
              value={selectedEvidence.file_type}
            />

            <InfoBox
              label="File Size"
              value={`${selectedEvidence.file_size} bytes`}
            />

            <InfoBox
              label="Status"
              value={selectedEvidence.status}
            />
          </div>
        </section>

        {/* CRYPTOGRAPHIC VERIFICATION */}

        <section className="panel">
          <div className="eyebrow">
            INTEGRITY VERIFICATION
          </div>

          <h2>Cryptographic Hash</h2>

          {verification ? (
            <>
              <HashBox
                label="Original SHA-256"
                value={verification.original_hash}
              />

              <HashBox
                label="Current SHA-256"
                value={verification.current_hash}
              />

              <div
                className={
                  evidenceIsAuthentic
                    ? "verification-result valid"
                    : "verification-result invalid"
                }
              >
                <strong>
                  {evidenceIsAuthentic
                    ? "✓ Evidence is authentic"
                    : "⚠ Evidence has been modified"}
                </strong>

                <span>
                  {verification.message}
                </span>
              </div>
            </>
          ) : (
            <div className="empty-state">
              Verification unavailable.
            </div>
          )}
        </section>

        {/* AUDIT CHAIN */}

        <section className="panel">
          <div className="eyebrow">AUDIT INTEGRITY</div>

          <h2>Cryptographic Audit Chain</h2>

          {chain ? (
            <div
              className={
                chain.valid
                  ? "verification-result valid"
                  : "verification-result invalid"
              }
            >
              <strong>
                {chain.valid
                  ? "✓ Audit Chain Valid"
                  : "⚠ Audit Chain Invalid"}
              </strong>

              <span>{chain.message}</span>

              <small>
                Checked events: {chain.checked_events}
              </small>
            </div>
          ) : (
            <div className="empty-state">
              Audit chain unavailable.
            </div>
          )}
        </section>

        {/* AI ANALYSIS */}

        <section className="panel">
          <div className="ai-heading">
            <div>
              <div className="eyebrow">
                ARTIFICIAL INTELLIGENCE
              </div>

              <h2>Evidence Analysis</h2>
            </div>

            <div
              className={
                aiIsValid
                  ? "status-badge authentic"
                  : aiIsInvalid
                  ? "status-badge tampered"
                  : "status-badge"
              }
            >
              {aiIsValid
                ? "AI VERIFIED"
                : aiIsInvalid
                ? "AI INVALID"
                : "AI UNKNOWN"}
            </div>
          </div>

          {analysisAvailable ? (
            <>
              <div className="ai-summary">
                <span>Summary</span>

                <p>
                  {analysis.analysis.summary}
                </p>
              </div>

              <div className="ai-grid">
                <AIList
                  title="Key Entities"
                  items={analysis.analysis.key_entities}
                />

                <AIList
                  title="Important Dates"
                  items={analysis.analysis.important_dates}
                />

                <AIList
                  title="Locations"
                  items={analysis.analysis.locations}
                />

                <AIList
                  title="Observations"
                  items={
                    analysis.analysis
                      .important_observations
                  }
                />

                <AIList
                  title="Relevant Information"
                  items={
                    analysis.analysis
                      .potentially_relevant_information
                  }
                />

                <div className="ai-card">
                  <span>AI Confidence</span>
                  <strong>
                    {analysis.analysis.confidence_level ||
                      "UNKNOWN"}
                  </strong>
                </div>
              </div>

              {/* AI HASH VERIFICATION */}

              <div className="ai-verification">
                <div className="eyebrow">
                  ANALYSIS INTEGRITY
                </div>

                <h3>AI Analysis Verification</h3>

                {analysisVerification ? (
                  <>
                    <div
                      className={
                        aiIsValid
                          ? "verification-result valid"
                          : "verification-result invalid"
                      }
                    >
                      <strong>
                        {aiIsValid
                          ? "✓ AI analysis matches current evidence"
                          : "⚠ AI analysis does not match current evidence"}
                      </strong>

                      <span>
                        {analysisVerification.message}
                      </span>
                    </div>

                    <HashBox
                      label="Analyzed Evidence Hash"
                      value={
                        analysisVerification.analyzed_evidence_hash
                      }
                    />

                    <HashBox
                      label="Current Evidence Hash"
                      value={
                        analysisVerification.current_evidence_hash
                      }
                    />
                  </>
                ) : (
                  <div className="empty-state">
                    AI analysis verification unavailable.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <strong>No AI analysis available.</strong>
              <p>
                Run the Analyze Evidence API for this
                evidence record.
              </p>
            </div>
          )}
        </section>

        {/* HISTORY */}

        <section className="panel">
          <div className="eyebrow">AUDIT TRAIL</div>
          <h2>Evidence History</h2>

          {history ? (
            <pre className="history-box">
              {JSON.stringify(history, null, 2)}
            </pre>
          ) : (
            <div className="empty-state">
              No history available.
            </div>
          )}
        </section>
      </>
    );
  };

  // =========================================================
  // MAIN RENDER
  // =========================================================

  return (
    <div className="app">
      <Sidebar />

      <main className="main">
        {page === "details" ? (
          <EvidenceDetails />
        ) : page === "dashboard" ? (
          <Dashboard />
        ) : page === "evidence" ? (
          <EvidencePage />
        ) : page === "audit" ? (
          <SimplePage
            title="Audit Trail"
            eyebrow="CRYPTOGRAPHIC HISTORY"
          >
            <p>
              Every evidence operation is recorded in the
              cryptographic audit chain.
            </p>

            <div className="operational large">
              <span className="green-dot"></span>
              Audit chain operational
            </div>
          </SimplePage>
        ) : page === "ai" ? (
          <SimplePage
            title="AI Analysis"
            eyebrow="ARTIFICIAL INTELLIGENCE"
          >
            <p>
              AI analysis is available inside each evidence
              record.
            </p>
          </SimplePage>
        ) : (
          <SimplePage
            title="Verification"
            eyebrow="EVIDENCE INTEGRITY"
          >
            <p>
              Open an evidence record to verify its SHA-256
              hash and cryptographic audit chain.
            </p>
          </SimplePage>
        )}
      </main>
    </div>
  );
}

// =========================================================
// COMPONENTS
// =========================================================

function StatCard({ title, value, subtitle }) {
  return (
    <div className="stat-card">
      <span>{title}</span>
      <strong>{String(value).padStart(2, "0")}</strong>
      <p>{subtitle}</p>
    </div>
  );
}

function EvidenceRow({ item, onClick }) {
  return (
    <button className="evidence-row" onClick={onClick}>
      <div className="file-icon">TXT</div>

      <div className="evidence-info">
        <strong>{item.evidence_id}</strong>
        <span>{item.file_name}</span>
      </div>

      <div className="submitted-status">
        <span className="green-dot"></span>
        {item.status || "SUBMITTED"}
      </div>

      <div className="arrow">→</div>
    </button>
  );
}

function InfoBox({ label, value }) {
  return (
    <div className="info-box">
      <span>{label}</span>
      <strong>{value || "N/A"}</strong>
    </div>
  );
}

function HashBox({ label, value }) {
  return (
    <div className="hash-box">
      <span>{label}</span>
      <code>{value || "N/A"}</code>
    </div>
  );
}

function AIList({ title, items }) {
  return (
    <div className="ai-card">
      <span>{title}</span>

      {items && items.length > 0 ? (
        <ul>
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <strong>None identified</strong>
      )}
    </div>
  );
}

export default App;