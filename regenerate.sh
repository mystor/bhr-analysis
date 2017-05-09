#!/bin/bash
for u in symbolicated-*; do 
    python generate.py "${u#symbolicated-}"
done
