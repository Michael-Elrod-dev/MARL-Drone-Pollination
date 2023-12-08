import pygame
import numpy as np
import random

# Constants
FIELD_SIZE = 1100
NUM_FLOWERS = 4500
VISION_RADIUS = 50
POLLINATION_RADIUS = 25
DRONE_SPEED = 2
MIN_CLUSTER_POINTS = 3  # Minimum number of points to form a cluster

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((FIELD_SIZE, FIELD_SIZE))
pygame.display.set_caption("Drone Pollination Simulation")

class Flower:
    def __init__(self):
        self.position = np.random.rand(2) * FIELD_SIZE
        self.seen = False
        self.clustered = False

flowers = [Flower() for _ in range(NUM_FLOWERS)]
clusters = []

class Drone:
    def __init__(self, start_x):
        self.position = np.array([start_x, FIELD_SIZE - 1])  # Position at the bottom
        self.direction = np.random.randn(2)
        self.direction /= np.linalg.norm(self.direction)

    def move(self):
        self.position += self.direction * DRONE_SPEED
        # If the drone hits the boundary, bounce it off by reversing the direction
        if not 0 <= self.position[0] <= FIELD_SIZE:
            self.direction[0] *= -1
        if not 0 <= self.position[1] <= FIELD_SIZE:
            self.direction[1] *= -1
        self.position = np.clip(self.position, 0, FIELD_SIZE)
        # Gradually change direction over time for smoother movement
        if random.random() < 0.1:  # 10% chance to gradually change direction
            turn_angle = random.uniform(-np.pi/4, np.pi/4)  # Turn by up to 45 degrees
            rotation_matrix = np.array([[np.cos(turn_angle), -np.sin(turn_angle)],
                                        [np.sin(turn_angle), np.cos(turn_angle)]])
            self.direction = np.dot(rotation_matrix, self.direction)
            self.direction /= np.linalg.norm(self.direction)


    def scan_and_cluster(self):
        for flower in flowers:
            if not flower.seen and np.linalg.norm(flower.position - self.position) <= VISION_RADIUS:
                flower.seen = True
                flower.clustered = self.check_cluster(flower)

    def check_cluster(self, flower):
        distance_threshold = 1.5 * POLLINATION_RADIUS

        if any(np.linalg.norm(flower.position - c['core'].position) < distance_threshold for c in clusters):
            return False  # Flower is within the radius of an existing cluster
        cluster_members = [f for f in flowers if np.linalg.norm(f.position - flower.position) <= POLLINATION_RADIUS]
        if len(cluster_members) >= MIN_CLUSTER_POINTS:
            clusters.append({'core': flower, 'members': cluster_members})
            return True
        return False

    def draw(self):
        # Draw clusters
        for cluster in clusters:
            core = cluster['core']
            pygame.draw.circle(screen, (128, 0, 0), (int(core.position[0]), int(core.position[1])), POLLINATION_RADIUS, 1)
            for flower in cluster['members']:
                pygame.draw.circle(screen, (255, 0, 0), (int(flower.position[0]), int(flower.position[1])), 3)
        # Draw flowers
        for flower in flowers:
            color = (200, 200, 200) if not flower.seen else (0, 0, 0)
            pygame.draw.circle(screen, color, (int(flower.position[0]), int(flower.position[1])), 3)

        # Draw the drone's vision and pollination radius
        pygame.draw.circle(screen, (0, 0, 255), (int(self.position[0]), int(self.position[1])), VISION_RADIUS, 1)
        pygame.draw.circle(screen, (0, 255, 0), (int(self.position[0]), int(self.position[1])), POLLINATION_RADIUS, 1)

# Drones in a line at the bottom
drones = [Drone(FIELD_SIZE / 6 * i) for i in range(6)]

# Initialize font
pygame.font.init()  # Initialize the font module
font = pygame.font.SysFont(None, 24)  # Create a font object
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for drone in drones:
        drone.move()
        drone.scan_and_cluster()

    screen.fill((255, 255, 255))
    for drone in drones:
        drone.draw()

    # Calculate counters and percentages
    flowers_seen = sum(flower.seen for flower in flowers)
    flowers_clusters = sum(flower.clustered for flower in flowers)
    seen_percentage = (flowers_seen / NUM_FLOWERS) * 100
    clustered_percentage = (flowers_clusters / flowers_seen) * 100

    # Render counters and draw them on the screen
    total_text = font.render(f'Total Flowers: {NUM_FLOWERS}', True, (0, 0, 0))
    seen_text = font.render(f'Flowers Seen: {flowers_seen} : {seen_percentage:.1f}%', True, (0, 0, 0))
    clustered_text = font.render(f'Flowers Clusters: {flowers_clusters}', True, (0, 0, 0))

    screen.blit(total_text, (10, 10))
    screen.blit(seen_text, (10, 30))
    screen.blit(clustered_text, (10, 50))

    pygame.display.flip()

pygame.quit()