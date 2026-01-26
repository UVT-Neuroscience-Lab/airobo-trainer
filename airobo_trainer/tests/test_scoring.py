"""
Quick test of the scoring system
"""

from airobo_trainer.models.scoring_system import ScoringSystem

def test_scoring():
    s = ScoringSystem()
    s.start_experiment()

    # Test scoring with high intention values
    s.change_instruction('left')
    s.update_intention(95, 10)  # High left intention
    s.change_instruction('right')
    s.update_intention(10, 95)  # High right intention

    score = s.end_experiment()
    print(f'Final score: {score}')

    # Test leaderboard submission
    s.submit_score("Test Player")
    leaderboard = s.get_leaderboard()
    print(f'Leaderboard entries: {len(leaderboard)}')
    for entry in leaderboard:
        print(f'  {entry}')

if __name__ == "__main__":
    test_scoring()
