package com.course.server;

import com.course.model.Course;
import com.course.model.EnrolledCourse;
import com.course.observer.AuditLoggerObserver;
import com.course.observer.StudentNotificationObserver;
import com.course.service.CourseManager;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/**
 * Built-in Java HTTP server serving REST API and static frontend assets.
 * Uses only standard Java SE library (com.sun.net.httpserver).
 */
public class SimpleHttpServer {
    private final int port;
    private final CourseManager courseManager;
    private final File publicDir;

    public SimpleHttpServer(int port, CourseManager courseManager) {
        this.port = port;
        this.courseManager = courseManager;
        this.publicDir = new File("public");
    }

    public void start() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        // API Contexts
        server.createContext("/api/courses", new CoursesHandler());
        server.createContext("/api/wishlist", new WishlistHandler());
        server.createContext("/api/schedule", new ScheduleHandler());
        server.createContext("/api/enroll", new EnrollHandler());
        server.createContext("/api/notifications", new NotificationsHandler());
        server.createContext("/api/audit", new AuditHandler());
        server.createContext("/api/strategies", new StrategiesHandler());

        // Static Web UI Files
        server.createContext("/", new StaticFileHandler());

        server.setExecutor(null); // default single/multi thread pool
        server.start();
        System.out.println("=================================================");
        System.out.println("  Student Course Management System is running!");
        System.out.println("  Access the Web UI at: http://localhost:" + port);
        System.out.println("=================================================");
    }

    // ================= Static File Handler =================

    private class StaticFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String path = exchange.getRequestURI().getPath();
            if (path == null || path.equals("/") || path.isEmpty()) {
                path = "/index.html";
            }

            File file = new File(publicDir, path.substring(1));
            if (!file.exists() || file.isDirectory()) {
                sendResponse(exchange, 404, "text/plain", "404 Not Found");
                return;
            }

            String contentType = "text/plain";
            if (path.endsWith(".html")) contentType = "text/html; charset=UTF-8";
            else if (path.endsWith(".css")) contentType = "text/css; charset=UTF-8";
            else if (path.endsWith(".js")) contentType = "application/javascript; charset=UTF-8";
            else if (path.endsWith(".json")) contentType = "application/json; charset=UTF-8";
            else if (path.endsWith(".svg")) contentType = "image/svg+xml";

            byte[] bytes = Files.readAllBytes(file.toPath());
            exchange.getResponseHeaders().set("Content-Type", contentType);
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(bytes);
            }
        }
    }

    // ================= /api/courses =================

    private class CoursesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            String method = exchange.getRequestMethod().toUpperCase();
            Map<String, String> params = parseQueryParams(exchange.getRequestURI().getQuery());

            if ("OPTIONS".equals(method)) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            if ("GET".equals(method)) {
                List<Course> courses = courseManager.getAllCourses();
                StringBuilder json = new StringBuilder("[");
                for (int i = 0; i < courses.size(); i++) {
                    Course c = courses.get(i);
                    boolean isWish = courseManager.isWishlisted(c.getId());
                    boolean isEnr = courseManager.isEnrolled(c.getId());

                    // Inject status flags into course JSON
                    String baseJson = c.toJson();
                    String fullJson = baseJson.substring(0, baseJson.length() - 1)
                            + ",\"isWishlisted\":" + isWish
                            + ",\"isEnrolled\":" + isEnr
                            + "}";

                    json.append(fullJson);
                    if (i < courses.size() - 1) json.append(",");
                }
                json.append("]");
                sendResponse(exchange, 200, "application/json", json.toString());
            } else if ("POST".equals(method)) {
                // Add Course
                String body = readRequestBody(exchange);
                Map<String, String> data = parseJsonOrForm(body);

                try {
                    String code = data.getOrDefault("code", "").trim();
                    String title = data.getOrDefault("title", "").trim();
                    String instructor = data.getOrDefault("instructor", "").trim();
                    int credits = Integer.parseInt(data.getOrDefault("credits", "3").trim());
                    double baseFee = Double.parseDouble(data.getOrDefault("baseFee", "400.0").trim());
                    String day = data.getOrDefault("day", "Monday").trim();
                    String startTime = data.getOrDefault("startTime", "09:00").trim();
                    String endTime = data.getOrDefault("endTime", "10:30").trim();
                    int capacity = Integer.parseInt(data.getOrDefault("capacity", "30").trim());
                    String description = data.getOrDefault("description", "").trim();

                    if (code.isEmpty() || title.isEmpty()) {
                        sendResponse(exchange, 400, "application/json", "{\"error\":\"Code and Title are required.\"}");
                        return;
                    }

                    Course added = courseManager.addCourse(code, title, instructor, credits, baseFee,
                            day, startTime, endTime, capacity, description);
                    sendResponse(exchange, 201, "application/json", added.toJson());
                } catch (Exception ex) {
                    sendResponse(exchange, 400, "application/json", "{\"error\":\"Invalid course data: " + Course.escapeJson(ex.getMessage()) + "\"}");
                }
            } else if ("PUT".equals(method)) {
                // Update Course
                String body = readRequestBody(exchange);
                Map<String, String> data = parseJsonOrForm(body);

                try {
                    int id = Integer.parseInt(data.getOrDefault("id", params.getOrDefault("id", "0")).trim());
                    String code = data.getOrDefault("code", "").trim();
                    String title = data.getOrDefault("title", "").trim();
                    String instructor = data.getOrDefault("instructor", "").trim();
                    int credits = Integer.parseInt(data.getOrDefault("credits", "3").trim());
                    double baseFee = Double.parseDouble(data.getOrDefault("baseFee", "400.0").trim());
                    String day = data.getOrDefault("day", "Monday").trim();
                    String startTime = data.getOrDefault("startTime", "09:00").trim();
                    String endTime = data.getOrDefault("endTime", "10:30").trim();
                    int capacity = Integer.parseInt(data.getOrDefault("capacity", "30").trim());
                    String description = data.getOrDefault("description", "").trim();

                    boolean updated = courseManager.updateCourse(id, code, title, instructor, credits,
                            baseFee, day, startTime, endTime, capacity, description);
                    if (updated) {
                        sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Course updated.\"}");
                    } else {
                        sendResponse(exchange, 404, "application/json", "{\"error\":\"Course not found.\"}");
                    }
                } catch (Exception ex) {
                    sendResponse(exchange, 400, "application/json", "{\"error\":\"Update failed: " + Course.escapeJson(ex.getMessage()) + "\"}");
                }
            } else if ("DELETE".equals(method)) {
                // Delete Course
                String idStr = params.get("id");
                if (idStr == null) {
                    String body = readRequestBody(exchange);
                    Map<String, String> data = parseJsonOrForm(body);
                    idStr = data.get("id");
                }

                if (idStr != null) {
                    try {
                        int id = Integer.parseInt(idStr);
                        boolean deleted = courseManager.deleteCourse(id);
                        if (deleted) {
                            sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Course deleted.\"}");
                        } else {
                            sendResponse(exchange, 404, "application/json", "{\"error\":\"Course not found.\"}");
                        }
                        return;
                    } catch (NumberFormatException ignored) {}
                }
                sendResponse(exchange, 400, "application/json", "{\"error\":\"Invalid Course ID.\"}");
            } else {
                sendResponse(exchange, 405, "application/json", "{\"error\":\"Method not allowed\"}");
            }
        }
    }

    // ================= /api/wishlist =================

    private class WishlistHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            String method = exchange.getRequestMethod().toUpperCase();
            Map<String, String> params = parseQueryParams(exchange.getRequestURI().getQuery());

            if ("OPTIONS".equals(method)) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            if ("GET".equals(method)) {
                List<Course> wishlist = courseManager.getWishlist();
                StringBuilder json = new StringBuilder("[");
                for (int i = 0; i < wishlist.size(); i++) {
                    json.append(wishlist.get(i).toJson());
                    if (i < wishlist.size() - 1) json.append(",");
                }
                json.append("]");
                sendResponse(exchange, 200, "application/json", json.toString());
            } else if ("POST".equals(method)) {
                String idStr = params.get("id");
                if (idStr == null) {
                    Map<String, String> data = parseJsonOrForm(readRequestBody(exchange));
                    idStr = data.get("id");
                }
                if (idStr != null) {
                    try {
                        int id = Integer.parseInt(idStr);
                        boolean added = courseManager.addToWishlist(id);
                        if (added) {
                            sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Added to wishlist.\"}");
                        } else {
                            sendResponse(exchange, 400, "application/json", "{\"error\":\"Could not add to wishlist or already present.\"}");
                        }
                        return;
                    } catch (NumberFormatException ignored) {}
                }
                sendResponse(exchange, 400, "application/json", "{\"error\":\"Valid id required.\"}");
            } else if ("DELETE".equals(method)) {
                String idStr = params.get("id");
                if (idStr == null) {
                    Map<String, String> data = parseJsonOrForm(readRequestBody(exchange));
                    idStr = data.get("id");
                }
                if (idStr != null) {
                    try {
                        int id = Integer.parseInt(idStr);
                        boolean removed = courseManager.removeFromWishlist(id);
                        if (removed) {
                            sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Removed from wishlist.\"}");
                        } else {
                            sendResponse(exchange, 404, "application/json", "{\"error\":\"Not in wishlist.\"}");
                        }
                        return;
                    } catch (NumberFormatException ignored) {}
                }
                sendResponse(exchange, 400, "application/json", "{\"error\":\"Valid id required.\"}");
            } else {
                sendResponse(exchange, 405, "application/json", "{\"error\":\"Method not allowed\"}");
            }
        }
    }

    // ================= /api/schedule =================

    private class ScheduleHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            String method = exchange.getRequestMethod().toUpperCase();
            Map<String, String> params = parseQueryParams(exchange.getRequestURI().getQuery());

            if ("OPTIONS".equals(method)) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            if ("GET".equals(method)) {
                List<EnrolledCourse> schedule = courseManager.getSchedule();
                StringBuilder json = new StringBuilder("[");
                for (int i = 0; i < schedule.size(); i++) {
                    json.append(schedule.get(i).toJson());
                    if (i < schedule.size() - 1) json.append(",");
                }
                json.append("]");
                sendResponse(exchange, 200, "application/json", json.toString());
            } else if ("DELETE".equals(method)) {
                String idStr = params.get("id");
                if (idStr == null) {
                    Map<String, String> data = parseJsonOrForm(readRequestBody(exchange));
                    idStr = data.get("id");
                }
                if (idStr != null) {
                    try {
                        int id = Integer.parseInt(idStr);
                        boolean dropped = courseManager.dropCourse(id);
                        if (dropped) {
                            sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Dropped course from schedule.\"}");
                        } else {
                            sendResponse(exchange, 404, "application/json", "{\"error\":\"Course not found in schedule.\"}");
                        }
                        return;
                    } catch (NumberFormatException ignored) {}
                }
                sendResponse(exchange, 400, "application/json", "{\"error\":\"Valid id required.\"}");
            } else {
                sendResponse(exchange, 405, "application/json", "{\"error\":\"Method not allowed\"}");
            }
        }
    }

    // ================= /api/enroll =================

    private class EnrollHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            String method = exchange.getRequestMethod().toUpperCase();

            if ("OPTIONS".equals(method)) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            if ("POST".equals(method)) {
                String body = readRequestBody(exchange);
                Map<String, String> data = parseJsonOrForm(body);

                try {
                    int courseId = Integer.parseInt(data.getOrDefault("courseId", "0").trim());
                    boolean addLab = Boolean.parseBoolean(data.getOrDefault("addLab", "false"));
                    boolean addHonors = Boolean.parseBoolean(data.getOrDefault("addHonors", "false"));
                    boolean addCert = Boolean.parseBoolean(data.getOrDefault("addCertificate", "false"));
                    String strategy = data.getOrDefault("strategy", "standard").trim();

                    String error = courseManager.enrollCourse(courseId, addLab, addHonors, addCert, strategy);
                    if (error == null) {
                        sendResponse(exchange, 200, "application/json", "{\"success\":true,\"message\":\"Course enrolled successfully!\"}");
                    } else {
                        sendResponse(exchange, 400, "application/json", "{\"error\":\"" + Course.escapeJson(error) + "\"}");
                    }
                } catch (Exception ex) {
                    sendResponse(exchange, 400, "application/json", "{\"error\":\"Enrollment failed: " + Course.escapeJson(ex.getMessage()) + "\"}");
                }
            } else {
                sendResponse(exchange, 405, "application/json", "{\"error\":\"Method not allowed\"}");
            }
        }
    }

    // ================= /api/notifications =================

    private class NotificationsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            if ("OPTIONS".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            List<StudentNotificationObserver.NotificationItem> list =
                    courseManager.getNotificationObserver().getNotifications();

            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                json.append(list.get(i).toJson());
                if (i < list.size() - 1) json.append(",");
            }
            json.append("]");
            sendResponse(exchange, 200, "application/json", json.toString());
        }
    }

    // ================= /api/audit =================

    private class AuditHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            if ("OPTIONS".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            List<AuditLoggerObserver.AuditEntry> log =
                    courseManager.getAuditLoggerObserver().getAuditLog();

            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < log.size(); i++) {
                json.append(log.get(i).toJson());
                if (i < log.size() - 1) json.append(",");
            }
            json.append("]");
            sendResponse(exchange, 200, "application/json", json.toString());
        }
    }

    // ================= /api/strategies =================

    private class StrategiesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            enableCors(exchange);
            if ("OPTIONS".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 204, "text/plain", "");
                return;
            }

            String json = "["
                    + "{\"key\":\"standard\",\"name\":\"Standard Student Plan\",\"discount\":0.0,\"desc\":\"Regular full university tuition rate.\"},"
                    + "{\"key\":\"merit\",\"name\":\"Academic Merit Scholarship\",\"discount\":0.30,\"desc\":\"Dean's list & academic excellence tier (30% tuition reduction).\"},"
                    + "{\"key\":\"financial_aid\",\"name\":\"Need-Based Financial Aid\",\"discount\":0.50,\"desc\":\"University endowment financial assistance (50% tuition reduction).\"},"
                    + "{\"key\":\"early_bird\",\"name\":\"Early Registration Incentive\",\"discount\":0.15,\"desc\":\"Priority registration deadline discount (15% tuition reduction).\"}"
                    + "]";
            sendResponse(exchange, 200, "application/json", json);
        }
    }

    // ================= HTTP Utilities =================

    private void enableCors(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }

    private void sendResponse(HttpExchange exchange, int statusCode, String contentType, String content) throws IOException {
        byte[] bytes = content.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", contentType);
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private String readRequestBody(HttpExchange exchange) throws IOException {
        InputStream is = exchange.getRequestBody();
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        byte[] data = new byte[1024];
        int nRead;
        while ((nRead = is.read(data, 0, data.length)) != -1) {
            buffer.write(data, 0, nRead);
        }
        return buffer.toString(StandardCharsets.UTF_8);
    }

    private Map<String, String> parseQueryParams(String query) {
        Map<String, String> map = new HashMap<>();
        if (query == null || query.isEmpty()) return map;
        for (String pair : query.split("&")) {
            String[] kv = pair.split("=");
            if (kv.length >= 2) {
                try {
                    map.put(URLDecoder.decode(kv[0], "UTF-8"), URLDecoder.decode(kv[1], "UTF-8"));
                } catch (Exception ignored) {}
            } else if (kv.length == 1) {
                map.put(kv[0], "");
            }
        }
        return map;
    }

    private Map<String, String> parseJsonOrForm(String body) {
        Map<String, String> map = new HashMap<>();
        if (body == null || body.trim().isEmpty()) return map;
        body = body.trim();

        // If JSON
        if (body.startsWith("{") && body.endsWith("}")) {
            String inner = body.substring(1, body.length() - 1);
            boolean inQuotes = false;
            StringBuilder current = new StringBuilder();
            List<String> tokens = new ArrayList<>();

            for (int i = 0; i < inner.length(); i++) {
                char c = inner.charAt(i);
                if (c == '"' && (i == 0 || inner.charAt(i - 1) != '\\')) {
                    inQuotes = !inQuotes;
                }
                if (c == ',' && !inQuotes) {
                    tokens.add(current.toString().trim());
                    current = new StringBuilder();
                } else {
                    current.append(c);
                }
            }
            if (current.length() > 0) {
                tokens.add(current.toString().trim());
            }

            for (String token : tokens) {
                int colonIdx = token.indexOf(':');
                if (colonIdx != -1) {
                    String k = token.substring(0, colonIdx).trim().replaceAll("^\"|\"$", "");
                    String v = token.substring(colonIdx + 1).trim();
                    if (v.startsWith("\"") && v.endsWith("\"") && v.length() >= 2) {
                        v = v.substring(1, v.length() - 1);
                    }
                    map.put(k, v);
                }
            }
        } else {
            // Form encoded
            map.putAll(parseQueryParams(body));
        }
        return map;
    }
}
