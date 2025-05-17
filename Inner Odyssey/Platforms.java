package com.example.advancedprogramming;

import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;

public class Platforms {
    double x,y,width,height;
    Color platformColor;

    Platforms(double x, double y, double width, double height){
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }
     public void draw(GraphicsContext gc){
        gc.setFill(Color.rgb(116,105,182));
        gc.fillRect(x,y,width,height);

     }
    public void render(){

    }

    public void update(){

    }
}
