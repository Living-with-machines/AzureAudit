from unittest.mock import patch

from az_audit.utils import login


def test_login():
    mock_password = patch(
        "az_audit.utils.getpass.getpass", return_value="this_is_a_password"
    )
    mock_input = patch("az_audit.utils.input")
    mock_input.side_effect = ["some-email@email.com", "test_sub"]
    mock_run = patch("az_audit.utils.run_cmd")
    mock_run.side_effect = [{"returncode": 0}, {"returncode": 0}]

    with mock_input as mock1, mock_password as mock2, mock_run as mock3:
        login()

        assert mock1.call_count == 2
        mock2.assert_called_once()
        assert mock2.return_value == "this_is_a_password"
        assert mock3.call_count == 2
