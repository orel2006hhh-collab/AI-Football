// Игровая логика
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Размеры карты
canvas.width = 1200;
canvas.height = 600;

// Состояние игры
let gameState = {
    health: 100,
    money: 800,
    currentWeapon: null,
    ammo: 30,
    reserveAmmo: 90,
    score: 0,
    enemyScore: 0,
    round: 1,
    alive: true,
    gameActive: false,
    enemies: [],
    currentMap: 'dust2'
};

// Данные оружия
const weapons = {
    pistol: { name: 'P250', damage: 25, fireRate: 400, price: 300, magSize: 13, maxAmmo: 52 },
    rifle: { name: 'AK-47', damage: 40, fireRate: 600, price: 2700, magSize: 30, maxAmmo: 90 },
    sniper: { name: 'AWP', damage: 100, fireRate: 48, price: 4750, magSize: 10, maxAmmo: 30 },
    shotgun: { name: 'XM1014', damage: 70, fireRate: 120, price: 2000, magSize: 7, maxAmmo: 28 }
};

// Позиция прицела
let mouseX = canvas.width / 2;
let mouseY = canvas.height / 2;

// Функция обновления HUD
function updateHUD() {
    document.getElementById('healthFill').style.width = `${gameState.health}%`;
    document.getElementById('healthText').innerHTML = `${Math.max(0, gameState.health)} HP`;
    document.getElementById('ammoText').innerHTML = `${gameState.ammo}/${gameState.reserveAmmo}`;
    document.getElementById('moneyText').innerHTML = gameState.money;
    document.getElementById('roundText').innerHTML = gameState.round;
    document.getElementById('scoreText').innerHTML = `${gameState.score} : ${gameState.enemyScore}`;
}

// Создание врагов
function spawnEnemies() {
    const count = 3 + Math.floor(Math.random() * 3);
    gameState.enemies = [];
    for (let i = 0; i < count; i++) {
        let side = Math.random() > 0.5 ? 'left' : 'right';
        let x = side === 'left' ? 50 + Math.random() * 200 : canvas.width - 50 - Math.random() * 200;
        let y = 100 + Math.random() * 400;
        gameState.enemies.push({
            x: x,
            y: y,
            health: 100,
            size: 30,
            agroRange: 300
        });
    }
}

// Отрисовка карты и объектов
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Пол
    ctx.fillStyle = '#3a3a3a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Линии для текстуры
    ctx.strokeStyle = '#555';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 50) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i % canvas.height);
        ctx.lineTo(canvas.width, i % canvas.height);
        ctx.stroke();
    }
    
    // Укрытия
    ctx.fillStyle = '#8B6914';
    ctx.fillRect(200, 200, 100, 200);
    ctx.fillRect(900, 300, 100, 200);
    ctx.fillStyle = '#4169E1';
    ctx.fillRect(500, 100, 80, 150);
    ctx.fillRect(700, 400, 80, 150);
    
    // Враги
    gameState.enemies.forEach(enemy => {
        ctx.fillStyle = '#8B0000';
        ctx.beginPath();
        ctx.rect(enemy.x - 15, enemy.y - 20, 30, 40);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px monospace';
        ctx.fillText('☠', enemy.x - 8, enemy.y - 5);
        // Полоска здоровья
        ctx.fillStyle = '#00ff00';
        ctx.fillRect(enemy.x - 15, enemy.y - 30, 30 * (enemy.health / 100), 5);
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(enemy.x - 15 + 30 * (enemy.health / 100), enemy.y - 30, 30 * (1 - enemy.health / 100), 5);
    });
    
    // Прицел
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(mouseX - 15, mouseY);
    ctx.lineTo(mouseX - 5, mouseY);
    ctx.moveTo(mouseX + 5, mouseY);
    ctx.lineTo(mouseX + 15, mouseY);
    ctx.moveTo(mouseX, mouseY - 15);
    ctx.lineTo(mouseX, mouseY - 5);
    ctx.moveTo(mouseX, mouseY + 5);
    ctx.lineTo(mouseX, mouseY + 15);
    ctx.stroke();
    
    // Круг прицела
    ctx.beginPath();
    ctx.arc(mouseX, mouseY, 8, 0, 2 * Math.PI);
    ctx.stroke();
}

// Выстрел
function shoot() {
    if (!gameState.alive || !gameState.gameActive) return;
    if (gameState.ammo <= 0) {
        // Перезарядка
        if (gameState.reserveAmmo > 0) {
            let weapon = weapons[gameState.currentWeapon];
            let needed = weapon.magSize - gameState.ammo;
            let take = Math.min(needed, gameState.reserveAmmo);
            gameState.ammo += take;
            gameState.reserveAmmo -= take;
            updateHUD();
        }
        return;
    }
    
    // Проверка попадания во врагов
    for (let i = 0; i < gameState.enemies.length; i++) {
        let enemy = gameState.enemies[i];
        let dx = mouseX - enemy.x;
        let dy = mouseY - enemy.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 40) {
            let weapon = weapons[gameState.currentWeapon];
            let damage = weapon.damage;
            enemy.health -= damage;
            
            if (enemy.health <= 0) {
                gameState.enemies.splice(i, 1);
                gameState.money += 300;
                updateHUD();
                i--;
            }
            break;
        }
    }
    
    gameState.ammo--;
    updateHUD();
    
    // Проверка победы в раунде
    if (gameState.enemies.length === 0) {
        winRound();
    }
}

// Победа в раунде
function winRound() {
    gameState.gameActive = false;
    gameState.score++;
    gameState.money += 800;
    updateHUD();
    document.getElementById('roundInfo').style.display = 'flex';
    document.querySelector('.round-title').innerHTML = 'РАУНД ВЫИГРАН!';
    document.querySelector('.round-desc').innerHTML = `Вы +800$ | Счёт: ${gameState.score} : ${gameState.enemyScore}`;
}

// Поражение в раунде
function loseRound() {
    gameState.gameActive = false;
    gameState.enemyScore++;
    updateHUD();
    document.getElementById('roundInfo').style.display = 'flex';
    document.querySelector('.round-title').innerHTML = 'ВЫ ПОГИБЛИ';
    document.querySelector('.round-desc').innerHTML = `Счёт: ${gameState.score} : ${gameState.enemyScore}`;
}

// Начать раунд
function startRound() {
    document.getElementById('roundInfo').style.display = 'none';
    gameState.alive = true;
    gameState.health = 100;
    gameState.gameActive = true;
    updateHUD();
    spawnEnemies();
    
    if (gameState.round > 5) {
        endGame();
    }
}

// Конец игры
function endGame() {
    gameState.gameActive = false;
    let isWin = gameState.score > gameState.enemyScore;
    document.getElementById('gameOver').style.display = 'flex';
    document.getElementById('gameOverTitle').innerHTML = isWin ? 'ПОБЕДА!' : 'ПОРАЖЕНИЕ!';
    document.getElementById('gameOverTitle').className = isWin ? 'game-over-title win' : 'game-over-title lose';
}

// Рестарт игры
function restartGame() {
    gameState = {
        health: 100,
        money: 800,
        currentWeapon: null,
        ammo: 30,
        reserveAmmo: 90,
        score: 0,
        enemyScore: 0,
        round: 1,
        alive: true,
        gameActive: false,
        enemies: [],
        currentMap: 'dust2'
    };
    document.getElementById('gameOver').style.display = 'none';
    document.getElementById('weaponSelector').style.display = 'flex';
    updateHUD();
}

// Выбор оружия
document.querySelectorAll('.weapon-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        let weapon = btn.dataset.weapon;
        let wData = weapons[weapon];
        if (gameState.money >= wData.price) {
            gameState.money -= wData.price;
            gameState.currentWeapon = weapon;
            gameState.ammo = wData.magSize;
            gameState.reserveAmmo = wData.maxAmmo;
            document.getElementById('weaponSelector').style.display = 'none';
            updateHUD();
            startRound();
        } else {
            alert(`Недостаточно денег! Нужно ${wData.price}$`);
        }
    });
});

// Инициализация событий
canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    mouseX = (e.clientX - rect.left) * scaleX;
    mouseY = (e.clientY - rect.top) * scaleY;
    mouseX = Math.min(Math.max(mouseX, 0), canvas.width);
    mouseY = Math.min(Math.max(mouseY, 0), canvas.height);
});

canvas.addEventListener('click', () => {
    shoot();
});

document.getElementById('startRoundBtn').addEventListener('click', () => {
    gameState.round++;
    updateHUD();
    startRound();
});

document.getElementById('restartBtn').addEventListener('click', () => {
    restartGame();
});

// Анимация
function animate() {
    draw();
    requestAnimationFrame(animate);
}

animate();

updateHUD();
