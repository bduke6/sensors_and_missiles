import pytest
from unittest.mock import patch, MagicMock
import src.simulation as simulation

@patch('src.simulation.Environment')
@patch('src.simulation.Config')
@patch('src.simulation.Missile')
@patch('src.simulation.Ship')
@patch('src.simulation.Aircraft')
@patch('src.simulation.Sensor')
@patch('src.simulation.LaunchEvent')
@patch('src.simulation.plt.show')
def test_simulation_run(mock_plt_show, mock_LaunchEvent, mock_Sensor, mock_Aircraft, mock_Ship, mock_Missile, mock_Config, mock_Environment):
    # Mock config values
    mock_config_instance = mock_Config.return_value
    mock_config_instance.get.side_effect = lambda key, default=None: {
        'entities.missile.position': [0, 0, 0],
        'entities.missile.velocity': [100, 0, 100],
        'entities.ship.position': [-500, 0, 0],
        'entities.ship.velocity': [10, 0, 0],
        'entities.aircraft.position': [0, 1000, 0],
        'entities.aircraft.velocity': [200, 0, 0],
        'sensors': [{'location': [0, 0], 'range': 1000}, {'location': [-500, 0], 'range': 1500}],
        'environment.max_time': 50,
        'environment.display_plot': False
    }[key]
    
    mock_config_instance.get_bool.side_effect = lambda key, default=False: {
        'environment.display_plot': False
    }[key]

    # Run the simulation script
    simulation.run_simulation('src/config.yaml')

    # Assertions to ensure components were called correctly
    mock_Environment.assert_called_once()
    mock_Config.assert_called_once_with('src/config.yaml')
    mock_Missile.assert_called_once_with(position=[0, 0, 0], velocity=[100, 0, 100])
    mock_Ship.assert_called_once_with(position=[-500, 0, 0], velocity=[10, 0, 0])
    mock_Aircraft.assert_called_once_with(position=[0, 1000, 0], velocity=[200, 0, 0])
    assert mock_Sensor.call_count == 2
    mock_LaunchEvent.assert_called_once_with(0, mock_Missile.return_value, None)
    mock_plt_show.assert_not_called()  # Ensure plot is not shown by default
