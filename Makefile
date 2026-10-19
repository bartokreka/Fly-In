# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: rbartok <rbartok@student.42wolfsburg.de    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/07 19:29:09 by rbartok           #+#    #+#              #
#    Updated: 2026/10/19 17:18:17 by rbartok          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

.SILENT:

install:
	uv sync

run:
# 	uv run python -m src --map maps/challenger/01_the_impossible_dream.txt
	uv run python -m src --map maps/easy/01_linear_path.txt
debug:
	uv run python -m pdb -m src

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -r {} +

lint:
	uv run python -m flake8 .
	uv run python -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs