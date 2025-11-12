from video_helpers import read_video, save_video
from trackers import Tracker
import cv2
from team_assigner import TeamAssigner


def main():
    # Read Video
    video_frames = read_video('input_videos/08fd33_4.mp4')


    # initialize tracker

    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(video_frames, read_from_stub= True,
                                       stub_path='stubs/tracks_stubs.pkl')
    


    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0],
                                    tracks['players'][0])
    
    # loop over each player in each frame and assign to correct team

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],
                                                 track['bound_box'],
                                                 player_id)
            
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]





    # Draw Output
    
    ## Draw object tracks

    output_video_frames = tracker.draw_annotations(video_frames, tracks)

    # Save Video

    #save_video(video_frames, 'output_videos/output_video.avi')
    
    save_video(output_video_frames, 'output_videos/output_video6.avi')

if __name__ == '__main__':
    main()