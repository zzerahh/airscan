<?php
$conn = mysqli_connect("localhost", "root", "Shaikh_6998", "hazman_sensor");

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

// Check if 'temperature' and 'humidity' are set in POST
if (!isset($_POST['temperature']) || !isset($_POST['humidity'])) {
    die("Missing temperature or humidity value.");
}
// Process POST request
$temperature = $_POST['temperature'];
$humidity = $_POST['humidity'];
$timestamp = date("Y-m-d H:i:s");  // Get the current timestamp

// Prepare and bind
$stmt = mysqli_prepare($conn, "INSERT INTO hazman_table (temperature, humidity, timestamp) VALUES (?, ?, ?)");
if ($stmt) {
    mysqli_stmt_bind_param($stmt, "dds", $temperature, $humidity, $timestamp);

    // Execute and check success
    if (mysqli_stmt_execute($stmt)) {
        echo "Success";
    } else {
        echo "Failed: " . mysqli_error($conn);
    }
    mysqli_stmt_close($stmt);
} else {
    echo "Failed to prepare statement: " . mysqli_error($conn);
}

mysqli_close($conn);
?>
 