package com.example.advancedprogramming;

import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;

public class HandleKey {
    private int curX, curY, width, height, moveX, moveY,prevX, prevY;
   private static Boolean moveRight = false;
   private static Boolean moveLeft = false;

    public void handleKeyPressed(KeyEvent e) {
        if (e.getCode() == KeyCode.A) {
            moveLeft = true;
            System.out.println(moveLeft);
        } else if (e.getCode() == KeyCode.D) {
            moveRight = true;
        } else if (e.getCode() == KeyCode.SPACE) {
            // Handle jump if needed
        }
    }

    public void handleKeyReleased(KeyEvent e) {
        if (e.getCode() == KeyCode.A) {
            moveLeft = false;
        } else if (e.getCode() == KeyCode.D) {
            moveRight = false;
        }
    }

    public boolean isMoveRight() {
        return moveRight;
    }

    public boolean isMoveLeft() {
        return moveLeft;
    }

    public  void setMoveRight(Boolean move){
        this.moveRight = move;
    }

    public void setMoveLeft(Boolean move){
        this.moveLeft = move;
    }
}
