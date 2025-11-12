from sklearn.cluster import KMeans

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}
        self.player_team_dict = {} # 1: 1,2 save a dict so we can save whether a player is team 1 or team 2

    def get_clustering_model(self, image):
        # Reshape the image to 2D Array

        image_2d = image.reshape(-1,3)

        # Preform K-means with 2 clusters
        kmeans = KMeans(n_clusters = 2, init="k-means++",n_init=1)
        kmeans.fit(image_2d)

        return kmeans

    def get_player_color(self,frame, bound_box):
        image = frame[int(bound_box[1]):int(bound_box[3]),int(bound_box[0]):int(bound_box[2])]

        top_half_image = image[0:int(image.shape[0]/2),:]

        # Get Clustering Model

        kmeans = self.get_clustering_model(top_half_image)

        # Get the cluster labels for each pixel

        labels = kmeans.labels_

        # Reshape the labels to the image shape

        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1])

        # Get the player cluster

        corner_clusters = [clustered_image[0,0], clustered_image[0,-1], clustered_image[-1,0], clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters), key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color

    def assign_team_color(self,frame, player_detections):

        player_colors = []
        for _, player_detection in player_detections.items():
            bound_box = player_detection["bound_box"]
            player_color = self.get_player_color(frame,bound_box)
            player_colors.append(player_color)

        
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]

    def get_player_team(self, frame, player_bound_box, player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]
        
        player_color = self.get_player_color(frame, player_bound_box)

        team_id = self.kmeans.predict([player_color.reshape(1,-1)])[0]
        team_id += 1 # team_id will be 0 or 1

        self.player_team_dict[player_id] = team_id  # saving to the dictionary so we don't have to keep running the k-means cluster for the next frame

        return team_id

