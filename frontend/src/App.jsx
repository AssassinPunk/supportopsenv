import { useEffect, useState } from "react";
import { resetEnv, getCurrentTicket, stepEnv } from "./api";
import "./App.css";

export default function App() {
  const [ticket, setTicket] = useState(null);
  const [result, setResult] = useState(null);

  const loadTicket = async () => {
    const data = await getCurrentTicket();
    setTicket(data.ticket);
  };

  useEffect(() => {
    loadTicket();
  }, []);

  const handleReset = async () => {
    await resetEnv();
    await loadTicket();
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
      payload = { message: "We are working on your issue." };
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
  };

  return (
    <div className="container">
      <h1>SupportOps Dashboard</h1>

      <button className="reset-btn" onClick={handleReset}>
        Reset Environment
      </button>

      {ticket ? (
        <div className="ticket-card">
          <h2>Ticket #{ticket.id}</h2>
          <p><strong>Customer:</strong> {ticket.customer_name}</p>
          <p><strong>Issue:</strong> {ticket.issue}</p>
          <p><strong>Category:</strong> {ticket.category}</p>
          <p><strong>Priority:</strong> {ticket.priority}</p>
          <p><strong>Status:</strong> {ticket.status}</p>
          <p><strong>Assigned To:</strong> {ticket.assigned_to || "Not assigned"}</p>
          <p><strong>Responded:</strong> {ticket.response_sent ? "Yes" : "No"}</p>
        </div>
      ) : (
        <p>All tickets are completed.</p>
      )}

    <div className="button-group">
      <button
        disabled={ticket?.assigned_to !== null}
        onClick={() => handleStep("assign")}
      >
        Assign
      </button>

      <button
        disabled={!ticket?.assigned_to || ticket?.response_sent}
        onClick={() => handleStep("respond")}
      >
        Respond
      </button>

      <button
        disabled={!ticket?.response_sent}
        onClick={() => handleStep("resolve")}
      >
        Resolve
      </button>
    </div>

      {result && (
        <div className="result-box">
          <h3>Last Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}