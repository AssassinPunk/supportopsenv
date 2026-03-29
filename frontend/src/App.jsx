import { useEffect, useState } from "react";
import { resetEnv, getCurrentTicket, stepEnv, autoStep, getAnalytics } from "./api";
import "./App.css";

export default function App() {
  const [ticket, setTicket] = useState(null);
  const [result, setResult] = useState(null);
  const [analytics, setAnalytics] = useState({
    reward_history: [],
    total_reward: 0,
    average_reward: 0,
    total_steps: 0,
  });

  const loadTicket = async () => {
    const data = await getCurrentTicket();
    setTicket(data.ticket);
  };

  const loadAnalytics = async () => {
    const data = await getAnalytics();
    setAnalytics(data);
  };

  useEffect(() => {
    const init = async () => {
      await resetEnv();
      await loadTicket();
      await loadAnalytics();
    };
    init();
  }, []);

  const handleReset = async () => {
    await resetEnv();
    await loadTicket();
    await loadAnalytics();
    setResult(null);
  };

  const handleStep = async (actionType) => {
    if (!ticket) return;

    let payload = {};

    if (actionType === "assign") {
      let team = "support_team";
      if (ticket.category === "billing") team = "billing_team";
      if (ticket.category === "authentication") team = "auth_team";
      if (ticket.category === "technical") team = "tech_team";
      payload = { team };
    }

    if (actionType === "respond") {
      payload = { message: "We are working on your issue and will update you shortly." };
    }

    if (actionType === "resolve") {
      payload = { resolution_note: "Issue resolved successfully." };
    }

    const res = await stepEnv({
      action_type: actionType,
      ticket_id: ticket.id,
      payload,
    });

    setResult(res);
    await loadTicket();
    await loadAnalytics();
  };

  const handleAutoStep = async () => {
    const res = await autoStep();
    setResult(res);
    await loadTicket();
    await loadAnalytics();
  };

  const canAssign = ticket && ticket.assigned_to === null;
  const canRespond = ticket && ticket.assigned_to && !ticket.response_sent;
  const canResolve = ticket && ticket.response_sent;

  return (
    <div className="app-shell">
      <div className="glow glow-1"></div>
      <div className="glow glow-2"></div>

      <div className="container">
        <div className="header-row">
          <div>
            <h1>SupportOps Dashboard</h1>
            <p className="subtitle">AI-powered support workflow simulator</p>
          </div>

          <div className="header-actions">
            <button className="secondary-btn" onClick={handleReset}>
              Reset Environment
            </button>
            <button className="primary-btn" onClick={handleAutoStep} disabled={!ticket}>
              Auto AI Play
            </button>
          </div>
        </div>

        <div className="grid-layout">
          <div className="left-column">
            <div className="panel ticket-panel">
              <h2>Current Ticket</h2>

              {ticket ? (
                <div className="ticket-card">
                  <div className="ticket-id">Ticket #{ticket.id}</div>
                  <div className="ticket-field"><span>Customer</span><strong>{ticket.customer_name}</strong></div>
                  <div className="ticket-field"><span>Issue</span><strong>{ticket.issue}</strong></div>
                  <div className="ticket-field"><span>Category</span><strong>{ticket.category}</strong></div>
                  <div className="ticket-field"><span>Priority</span><strong>{ticket.priority}</strong></div>
                  <div className="ticket-field"><span>Status</span><strong>{ticket.status}</strong></div>
                  <div className="ticket-field"><span>Assigned To</span><strong>{ticket.assigned_to || "Not assigned"}</strong></div>
                  <div className="ticket-field"><span>Responded</span><strong>{ticket.response_sent ? "Yes" : "No"}</strong></div>
                </div>
              ) : (
                <div className="empty-state">All tickets are completed.</div>
              )}
            </div>

            <div className="panel">
              <h2>Manual Controls</h2>
              <div className="button-group">
                <button onClick={() => handleStep("assign")} disabled={!canAssign}>
                  Assign
                </button>
                <button onClick={() => handleStep("respond")} disabled={!canRespond}>
                  Respond
                </button>
                <button onClick={() => handleStep("resolve")} disabled={!canResolve}>
                  Resolve
                </button>
              </div>
            </div>

            {result && (
              <div className="panel">
                <h2>Last Result</h2>

                <div className="result-grid">
                  <div className="result-card">
                    <span>Action Type</span>
                    <strong>{result.action?.action_type || "N/A"}</strong>
                  </div>

                  <div className="result-card">
                    <span>Ticket ID</span>
                    <strong>{result.action?.ticket_id || "N/A"}</strong>
                  </div>

                  <div className="result-card">
                    <span>Reward</span>
                    <strong>{result.result?.reward ?? result.reward ?? "N/A"}</strong>
                  </div>

                  <div className="result-card">
                    <span>Done</span>
                    <strong>
                      {(result.result?.done ?? result.done) ? "Yes" : "No"}
                    </strong>
                  </div>
                </div>

                <div className="result-details">
                  <div className="detail-row">
                    <span>Message</span>
                    <strong>
                      {result.result?.observation?.message ||
                        result.observation?.message ||
                        "No message"}
                    </strong>
                  </div>

                  <div className="detail-row">
                    <span>Payload</span>
                    <strong>
                      {result.action?.payload
                        ? Object.entries(result.action.payload)
                            .map(([key, value]) => `${key}: ${value}`)
                            .join(" | ")
                        : "No payload"}
                    </strong>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="right-column">
            <div className="panel analytics-panel">
              <h2>Reward Analytics</h2>

              <div className="stats-grid">
                <div className="stat-card">
                  <span>Total Reward</span>
                  <strong>{analytics.total_reward?.toFixed(2)}</strong>
                </div>

                <div className="stat-card">
                  <span>Average Reward</span>
                  <strong>{analytics.average_reward?.toFixed(2)}</strong>
                </div>

                <div className="stat-card">
                  <span>Total Steps</span>
                  <strong>{analytics.total_steps}</strong>
                </div>

                <div className="stat-card">
                  <span>Resolved Tickets</span>
                  <strong>{ticket ? "In Progress" : "Completed"}</strong>
                </div>
              </div>

              <div className="chart-panel">
                <h3>Reward History</h3>
                <div className="bar-chart">
                  {analytics.reward_history?.length > 0 ? (
                    analytics.reward_history.map((value, index) => (
                      <div key={index} className="bar-wrapper">
                        <div
                          className={`bar ${value >= 0 ? "positive" : "negative"}`}
                          style={{ height: `${Math.max(Math.abs(value) * 60, 12)}px` }}
                          title={`Step ${index + 1}: ${value}`}
                        ></div>
                        <span>{index + 1}</span>
                      </div>
                    ))
                  ) : (
                    <p className="muted">No rewards yet.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}