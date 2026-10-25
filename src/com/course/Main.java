package com.course;

import com.course.server.SimpleHttpServer;
import com.course.service.CourseManager;

/**
 * Main application launcher for the Student Course Management System.
 */
public class Main {
    public static void main(String[] args) {
        int port = 8080;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException ignored) {}
        }

        try {
            CourseManager courseManager = new CourseManager();
            SimpleHttpServer server = new SimpleHttpServer(port, courseManager);
            server.start();
        } catch (Exception e) {
            System.err.println("Failed to start server: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
