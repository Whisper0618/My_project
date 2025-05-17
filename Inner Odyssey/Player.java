package com.example.advancedprogramming;

import javafx.animation.AnimationTimer;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;

import java.io.FileInputStream;
import java.io.FileNotFoundException;

public class Player {
    private int curX, curY, width, height, moveX, moveY,prevX, prevY;
    private Image image;
    private ImageView imageView;
    public HandleKey key;


    public Player(int startX, int startY, String imagePath, HandleKey key) {
        this.key = key;
        curX = startX;
        curY = startY;
        try {
            image = new Image(new FileInputStream(imagePath));
            width = (int) image.getWidth();
            height = (int) image.getHeight();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        AnimationTimer timer = new AnimationTimer() {
            @Override
            public void handle(long now) {
                update();
            }
        };
        timer.start();
    }

    public void draw(GraphicsContext gc) {
        gc.clearRect(0, 0, 1200, 900);
        gc.drawImage(image, curX, curY);
    }


    public void update() {
        if (key.isMoveLeft()) {
            System.out.println(key.isMoveLeft());
            moveLeft();
        } else if (key.isMoveRight()) {
            this.moveRight();
        } else {
//            this.stop();
        }
        updatePosition();
    }

    public void moveRight() {
        moveX=5;
    }

    public void moveLeft() {
        moveX=-5;
    }

    public void updatePosition() {
        prevX = curX;
        prevY = curY;
        curX += moveX;
        curY += moveY;
        moveX=0;
//        if (!onGround) {
//            velocityY += 1;
//        }
    }
}

