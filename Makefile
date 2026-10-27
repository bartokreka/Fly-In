# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: rbartok <rbartok@student.42wolfsburg.de    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/07 19:29:09 by rbartok           #+#    #+#              #
#    Updated: 2026/10/27 11:23:42 by rbartok          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

.SILENT:

install:
	uv sync

run:
# 	uv run python -m src --map maps/easy/01_linear_path.txt
	uv run python -m src --map maps/easy/02_simple_fork.txt
# 	uv run python -m src --map maps/easy/03_basic_capacity.txt
# 	uv run python -m src --map maps/medium/01_dead_end_trap.txt
# 	uv run python -m src --map maps/medium/02_circular_loop.txt
# 	uv run python -m src --map maps/medium/03_priority_puzzle.txt
# 	uv run python -m src --map maps/hard/01_maze_nightmare.txt
# 	uv run python -m src --map maps/hard/02_capacity_hell.txt
# 	uv run python -m src --map maps/hard/03_ultimate_challenge.txt
# 	uv run python -m src --map maps/challenger/01_the_impossible_dream.txt
# 	uv run python -m src --map maps/custom/1_linear_restricted.txt

debug:
	uv run python -m pdb -m src --map maps/custom/1_linear_restricted.txt

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -r {} +

lint:
	uv run python -m flake8 .
	uv run python -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs