from app.env import SupportOpsEnv
from app.models import Action


def test_env_reset():
    env = SupportOpsEnv()
    result = env.reset()

    assert result.done is False
    assert result.observation.ticket is not None
    assert result.reward == 0.0


def test_env_step_respond_updates_ticket():
    env = SupportOpsEnv()
    env.reset()

    action = Action(
        action_type="respond",
        ticket_id=1,
        payload={"message": "We are checking your payment issue."}
    )
    result = env.step(action)

    assert "error" not in result.info
    assert env.tickets[0].response_sent is True
    assert result.done is False