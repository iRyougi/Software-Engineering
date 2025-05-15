-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-04-30 16:33:44
-- 服务器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `email`
--

-- --------------------------------------------------------

--
-- 表的结构 `emails`
--

CREATE TABLE `emails` (
  `id` int(11) NOT NULL,
  `sender` varchar(255) NOT NULL,
  `recipient` varchar(255) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `body` text NOT NULL,
  `sent_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `emails`
--

INSERT INTO `emails` (`id`, `sender`, `recipient`, `subject`, `body`, `sent_at`) VALUES
(1, 'noreply@edba.com', 'user@example.com', 'Verification Code', 'Your verification code is: 7X9T2P.', '2025-04-30 20:14:29'),
(2, 'noreply@edba.com', 'user@example.com', 'Verification Failed', 'Verification failed. Please try again.', '2025-04-30 20:14:29'),
(3, 'noreply@edba.com', 'user@example.com', 'Verification Success', 'Your account has been verified successfully!', '2025-04-30 20:14:29'),
(4, 'admin@edba.com', 'applicant@example.com', 'Registration Approved', 'Your registration has been approved. Welcome to E-DBA!', '2025-04-30 20:14:29'),
(5, 'admin@edba.com', 'applicant@example.com', 'Registration Rejected', 'Your registration was rejected due to incomplete documentation.', '2025-04-30 20:14:29'),
(6, 'support@edba.com', 'user@example.com', 'Reply to Your Question', 'Your question has been resolved. Check the response in your workspace.', '2025-04-30 20:14:29');

--
-- 转储表的索引
--

--
-- 表的索引 `emails`
--
ALTER TABLE `emails`
  ADD PRIMARY KEY (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `emails`
--
ALTER TABLE `emails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
