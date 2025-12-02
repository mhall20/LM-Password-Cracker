# LM-Password-Cracker

This is a school project aimed at cracking legacy Windows LM-hash passwords using a hand-made DES implementation and a custom rainbow table.

## Table of Contents
- [Project Overview](#overview)
- [Features](#features)
- [Usage](#usage)

## Project Overview
The LM Password Cracker is a tool that attempts to recover plaintext passwords from LM-hashes. It uses a word list of all words in the English dictionary to generate candidate passwords; which is accompanied with a precomputed list of different types of common password methods.

It combines these two lists and uses DES to create a rainbow table of LM-hashes and their plaintext, and then compares these to the given passwords that it is assigned to crack.

The rainbow table takes multiple hours to create, but once created, it can be used repeatedly for fast cracking. In the future, I would like to optimize the rainbow table creation by implementing processes for faster times.

## Features
- Custom DES implementation: instead of an external library, it uses a DES implementation created by me.
- Dictionary-based cracking: uses a precomputer dictionary for cracking to speed up the process of matching vs brute force
- Modular: the code is split into separate files to ease readability and modification

## Usage
1. Import a txt file into the folder named pwdump that has a list of LM-hash passwords to crack
2. - python 2024_Fall_passwordcracker.py
