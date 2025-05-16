-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 12, 2025 at 09:27 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `testdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `activityrecord`
--

CREATE TABLE `activityrecord` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `action` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bankaccount`
--

CREATE TABLE `bankaccount` (
  `id` int(11) NOT NULL,
  `account` varchar(30) NOT NULL,
  `balance` decimal(15,2) DEFAULT 0.00,
  `password` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bankaccount`
--

INSERT INTO `bankaccount` (`id`, `account`, `balance`, `password`) VALUES
(1, 'ACCrich', 999999.99, '123'),
(2, 'ACCpoor', 20.75, '456'),
(3, 'ProjectFundSDW', 5000000.00, '789');

-- --------------------------------------------------------

--
-- Table structure for table `policy`
--

CREATE TABLE `policy` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `explanation` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `policy`
--

INSERT INTO `policy` (`id`, `title`, `content`, `explanation`) VALUES
(1, 'Privacy Policy', 'This policy outlines how user data is collected and used.', 'Explains the measures taken to protect user privacy.'),
(2, 'Terms of Service', 'Users must agree to these terms to use the platform.', 'Details the legal obligations of users and the service provider.'),
(3, 'Cookie Policy', 'We use cookies to enhance user experience.', 'Describes the types of cookies used and their purposes.'),
(4, 'Refund Policy', 'Refunds are available within 30 days of purchase.', 'Clarifies conditions under which refunds are granted.'),
(5, 'Content Guidelines', 'Users must follow community guidelines when posting content.', 'Ensures a safe and respectful environment for all users.');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `usertype` varchar(50) DEFAULT NULL,
  `level` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `email`, `usertype`, `level`) VALUES
(1, 'alice', '123456789', 'alice@example.com', 'T-Admin', 0),
(2, 'bob', 'abcdefg', 'bob@example.com', 'E-Admin', 0),
(3, 'charlie', '789', 'charlie@example.com', 'Public Data Consumer', 1),
(4, 'diana', '456', 'diana@example.com', 'Private Data Consumer', 2),
(5, 'steven', '123', 'steven@example.com', 'Private Data Provider', 3);

-- --------------------------------------------------------

--
-- Table structure for table `userquestion`
--

CREATE TABLE `userquestion` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `question` text NOT NULL,
  `answer` text DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/main
-- --------------------------------------------------------

--
-- Table structure for table `thesis`
--

CREATE TABLE `thesis` (
  `id` int(11) NOT NULL,
  `author` varchar(30) NOT NULL,
  `title` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bankaccount`
--

INSERT INTO `thesis` (`id`, `author`, `title`) VALUES
(1, 'Jack', 'About Software Development Workshop'),
(2, 'Marry', 'About Software Engineering'),
(3, 'Tom', 'About Machine Learning');

-- --------------------------------------------------------

--
-- Table structure for table `thesis`
--

CREATE TABLE `studentrecord` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `gender` varchar(100) NOT NULL,
  `dateofbirth` varchar(30) NOT NULL,
  `enrollmentyear` varchar(30) NOT NULL,
  `graduationyear` varchar(30) NOT NULL, 
  `gpa` varchar(30) NOT NULL 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bankaccount`
--

INSERT INTO `studentrecord` (`id`, `name`, `gender`, `dateofbirth`, `enrollmentyear`, `graduationyear`, `gpa`) VALUES
(1, 'Jack', 'male', '2000.01.01', '2018', '2022', '3.5'),
(2, 'Marry', 'female', '2001.01.01', '2019', '2023', '3.3'),
(3, 'Tom', 'male', '2000.03.01', '2018', '2022', '3.2');
<<<<<<< HEAD
>>>>>>> origin/main
=======
>>>>>>> origin/main
--
-- Indexes for dumped tables
--

--
-- Indexes for table `activityrecord`
--
ALTER TABLE `activityrecord`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bankaccount`
--
ALTER TABLE `bankaccount`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `account` (`account`);

--
-- Indexes for table `policy`
--
ALTER TABLE `policy`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `userquestion`
--
ALTER TABLE `userquestion`
  ADD PRIMARY KEY (`id`);

--
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/main
-- Indexes for table `user`
--
ALTER TABLE `studentrecord`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `userquestion`
--
ALTER TABLE `thesis`
  ADD PRIMARY KEY (`id`);


--
<<<<<<< HEAD
>>>>>>> origin/main
=======
>>>>>>> origin/main
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activityrecord`
--
ALTER TABLE `activityrecord`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bankaccount`
--
ALTER TABLE `bankaccount`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `policy`
--
ALTER TABLE `policy`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `userquestion`
--
ALTER TABLE `userquestion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
<<<<<<< HEAD
<<<<<<< HEAD
COMMIT;

=======
=======
>>>>>>> origin/main

--
-- AUTO_INCREMENT for table `thesis`
--
ALTER TABLE `thesis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `studentrecord`
--
ALTER TABLE `studentrecord`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;


<<<<<<< HEAD
>>>>>>> origin/main
=======
>>>>>>> origin/main
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
