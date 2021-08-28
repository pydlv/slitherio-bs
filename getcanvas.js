// noinspection JSAnnotator

function mapSnake(snake) {
    if (snake === null) return null;
    return {
        x: snake.xx,
        y: snake.yy,
        color: snake.cs,
        // points: snake.pts.filter(point => point.da <= 0.2).map(point => [point.xx, point.yy])
        points: snake.pts.filter(pt => !pt.dying).map(point => {
            return {
                x: point.xx,
                y: point.yy
                // dying: point.dying
            }
        }),
        facing_angle: snake.ang
    }
}

function mapFood(food) {
    if (food === null) return null;
    return {
        x: food.xx,
        y: food.yy,
        size: food.sz
    }
}

return {
    playing: window.playing,
    snake: window.snake && {
        ...mapSnake(window.snake),
        length: Math.floor(15 * (window.fpsls[window.snake.sct] + window.snake.fam /
                window.fmlts[window.snake.sct] - 1) - 5)
    },
    snakes: window.snakes.map(mapSnake),
    foods: window.foods.filter(food => food !== null && food.sz > 7).map(mapFood)
    // preys: window.preys
}