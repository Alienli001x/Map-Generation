import numpy as np
import matplotlib.pyplot as plt
import os

# 地图尺寸
width = 100
height = 100

# 地形类型
TERRAIN = {
    "grass": 1,  # 草地
    "water": 2,  # 水域
    "forest": 3,  # 森林
    "soil": 4,  # 土地
    "house": 5,  # 房屋
}

# 颜色映射
COLORS = {
    TERRAIN["grass"]: "#7CFC00",
    TERRAIN["water"]: "#1E90FF",
    TERRAIN["forest"]: "#228B22",
    TERRAIN["soil"]: "#8B4513",
    TERRAIN["house"]: "#FFD700",
}

# 初始化地图
def initialize_map(width, height):
    return np.full((height, width), TERRAIN["grass"], dtype=int)

# 生成垂直河流路径
def generate_vertical_river(game_map):
    x, y = game_map.shape[1] // 2, 0  # 从顶部中央开始
    game_map[y, x] = TERRAIN["water"]

    while y < game_map.shape[0] - 1:  # 确保河流贯穿整个地图
        direction = np.random.choice(["down", "left", "right"], p=[0.7, 0.15, 0.15])
        if direction == "down" and y < game_map.shape[0] - 1:
            y += 1
        elif direction == "left" and x > 0:
            x -= 1
        elif direction == "right" and x < game_map.shape[1] - 1:
            x += 1
        game_map[y, x] = TERRAIN["water"]

# 生成水平河流路径
def generate_horizontal_river(game_map):
    x, y = 0, game_map.shape[0] // 2  # 从左侧中央开始
    game_map[y, x] = TERRAIN["water"]

    while x < game_map.shape[1] - 1:  # 确保河流贯穿整个地图
        direction = np.random.choice(["right", "up", "down"], p=[0.7, 0.15, 0.15])
        if direction == "right" and x < game_map.shape[1] - 1:
            x += 1
        elif direction == "up" and y > 0:
            y -= 1
        elif direction == "down" and y < game_map.shape[0] - 1:
            y += 1
        game_map[y, x] = TERRAIN["water"]

# 生成其他地形
def populate_terrain(game_map):
    center_x, center_y = game_map.shape[1] // 2, game_map.shape[0] // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)

    for y in range(game_map.shape[0]):
        for x in range(game_map.shape[1]):
            if game_map[y, x] == TERRAIN["grass"]:  # 只替换草地
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                probability = distance / max_distance
                if np.random.random() < probability * 0.5:  # 调低土地概率
                    game_map[y, x] = TERRAIN["soil"]
                elif np.random.random() < (1 - probability) * 1.2:  # 增加森林概率
                    game_map[y, x] = TERRAIN["forest"]

# 在水域附近生成房屋
def generate_houses(game_map):
    house_count = 0
    for y in range(game_map.shape[0]):
        for x in range(game_map.shape[1]):
            if game_map[y, x] == TERRAIN["grass"]:
                # 检查是否在水域旁边
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < game_map.shape[0] and 0 <= nx < game_map.shape[1]:
                        if game_map[ny, nx] == TERRAIN["water"] and np.random.random() < 0.1:
                            game_map[y, x] = TERRAIN["house"]
                            house_count += 1
                            break
    return house_count

# 计算适应度
def calculate_fitness(game_map):
    house_positions = np.argwhere(game_map == TERRAIN["house"])
    if len(house_positions) < 2:
        return 0
    distances = [
        np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        for i, (y1, x1) in enumerate(house_positions)
        for y2, x2 in house_positions[i + 1:]
    ]
    return len(distances) / (sum(distances) + 1e-5)

# 可视化并保存地图
def visualize_and_save_map(game_map, filename):
    color_map = np.zeros((game_map.shape[0], game_map.shape[1], 3))
    for terrain, color in COLORS.items():
        color_map[game_map == terrain] = plt.cm.colors.to_rgb(color)
    plt.imshow(color_map)
    plt.axis("off")

    # 添加图例
    legend_elements = [
        plt.Line2D([0], [0], color=color, lw=4, label=terrain)
        for terrain, color in zip(["Grass", "Water", "Forest", "Soil", "House"], COLORS.values())
    ]
    plt.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=5, frameon=False)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

# 主函数
if __name__ == "__main__":
    # 创建存储地图的文件夹
    output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "map")
    os.makedirs(output_folder, exist_ok=True)

    fitness_scores = []
    map_count = 0

    while len(fitness_scores) < 10:
        map_count += 1
        # 初始化地图
        game_map = initialize_map(width, height)

        # 生成垂直贯穿地图的河流
        generate_vertical_river(game_map)

        # 生成水平贯穿地图的河流
        generate_horizontal_river(game_map)

        # 填充其他地形
        populate_terrain(game_map)

        # 在水域附近生成房屋
        house_count = generate_houses(game_map)

        # 计算适应度
        fitness = calculate_fitness(game_map)
        if fitness > 0.025:
            fitness_scores.append((map_count, fitness))

            # 保存地图
            filename = os.path.join(output_folder, f"map_{map_count}.png")
            visualize_and_save_map(game_map, filename)

    # 输出适应度前 10 的图号
    fitness_scores.sort(key=lambda x: x[1], reverse=True)
    print("Top 10 maps by fitness:")
    for rank, (map_id, fitness) in enumerate(fitness_scores, start=1):
        print(f"Rank {rank}: Map {map_id} with fitness {fitness:.4f}")

    print(f"Maps saved to {output_folder}")
