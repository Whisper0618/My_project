package com.example.advancedprogramming;

import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;
import javafx.scene.layout.Pane;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class GameStage extends Pane {
    Image image;
    Canvas canvas;
    Player player;
    Platforms[] platform;

    GameStage() {
        platform = new Platforms[]{
                new Platforms(50, 400, 700, 20)
        };
        try {
            image = new Image(Files.newInputStream(Path.of("lvl1.png")));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        canvas = new Canvas(1200, 800);
        this.getChildren().add(canvas);

        HandleKey key = new HandleKey();
        player = new Player(50, 50, "character.jpg", key);
        AnimationTimer timer = new AnimationTimer() {
            @Override
            public void handle(long now) {
//                canvas.getGraphicsContext2D().clearRect(0, 0, canvas.getWidth(), canvas.getHeight());
                update();
                render(canvas.getGraphicsContext2D());
            }
        };

        timer.start();
        this.setFocusTraversable(true);
        this.requestFocus();
    }

    public void update(){
        player.update();
    }

    public void render(GraphicsContext gc){
        gc.drawImage(image, 0, 0, 1249, 815);
        player.draw(gc);
        for(Platforms platforms : platform){
            platforms.draw(gc);
        }

    }

}
