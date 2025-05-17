package com.example.advancedprogramming;

import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;

import java.awt.event.KeyListener;
import java.io.IOException;

public class HelloApplication extends Application {

    @Override
    public void start(Stage primaryStage) throws IOException {
        GameStage stage1 = new GameStage();
        stage1.requestFocus();
        Scene scene = new Scene(stage1);
        HandleKey key = new HandleKey();
        scene.setOnKeyPressed(key::handleKeyPressed);
        scene.setOnKeyReleased(key::handleKeyReleased);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Simple Game");
        primaryStage.show();

    }

    public static void main(String[] args) {
        launch();
    }
}
