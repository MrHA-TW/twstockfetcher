# Gemini Agent Instructions

This document provides instructions for the Gemini AI agent to interact with this project.

## Directory Overview

This is a non-code project that serves as a workspace for managing and specifying software development features. The main purpose of this directory is to define features, create implementation plans, and generate tasks for AI-driven development.

### Key Files and Directories

*   `specs/`: This directory contains subdirectories for each feature, named according to the feature branch (e.g., `001-feature-name`). Each feature directory contains:
    *   `spec.md`: The feature specification, outlining the "what" of the feature.
    *   `plan.md`: The implementation plan, detailing the "how" of the feature.
    *   `tasks.md`: A list of tasks to be executed to implement the feature.
*   `.specify/`: This directory contains the configuration and scripts for the feature management workflow.
    *   `scripts/bash/`: Contains shell scripts for managing features, plans, and tasks.
    *   `templates/`: Contains templates for `spec.md`, `plan.md`, and other files.
*   `GEMINI.md`: This file, providing instructions for the Gemini AI agent.

## Development Workflow

The development workflow is feature-driven and managed through a set of shell scripts.

1.  **Create a new feature:** A new feature is created by running the `create-new-feature.sh` script. This script creates a new git branch, a corresponding directory in `specs/`, and a `spec.md` file from a template.
2.  **Define the feature:** The `spec.md` file is then filled out to define the feature's requirements, user stories, and acceptance criteria.
3.  **Create an implementation plan:** Once the specification is complete, the `setup-plan.sh` script is used to create a `plan.md` file. This file outlines the technical details of the implementation.
4.  **Generate tasks:** After the plan is finalized, a `tasks.md` file is generated, which contains a list of tasks to be executed to implement the feature.

## Commands

The following are the key commands for managing the development workflow:

*   `.specify/scripts/bash/create-new-feature.sh <feature_description>`: Creates a new feature branch and directory.
*   `.specify/scripts/bash/setup-plan.sh`: Creates a `plan.md` file for the current feature.
*   `.specify/scripts/bash/check-task-prerequisites.sh`: Checks if the prerequisites for task generation are met.
*   `.specify/scripts/bash/get-feature-paths.sh`: Prints the paths for the current feature.
*   `.specify/scripts/bash/update-agent-context.sh`: Updates the agent context files (e.g., `GEMINI.md`) with the latest project information.
