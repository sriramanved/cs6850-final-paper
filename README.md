# Multi-Drone Delivery Optimization: A Heuristic Approach

## CS 6850: The Structure of Information Networks @ Cornell University, Fall 2023

### Overview
In the transformative field of last-mile delivery, the integration of drones has emerged as a pivotal innovation. Our research, conducted under the guidance of Prof. Jon Kleinberg, focuses on optimizing drone-assisted delivery systems. This repository hosts our paper titled "On the Multi-Drone Delivery Problem" and the corresponding code, which explores novel algorithmic solutions to enhance the efficiency of these systems.

### Abstract
Drone delivery systems have emerged as a transformative solution to the challenges inherent in last-mile delivery—the final and most costly phase of the supply chain that moves products from a warehouse to the customer’s doorstep. This paper focuses on tying recent algorithmic developments to foundational models in this area. We first introduce two papers, the first of which has laid the groundwork in this domain and a second that proposes new avenues for further study. We then explore how the problem is transformed in various cities by studying its underlying graph structure. Leveraging these insights, we formulate a novel mathematical model with the ability to account for the use of multiple drones in the delivery process. Through data analysis, we demonstrate the improved performance of our model in diverse real-
world scenarios, highlighting its potential to reduce delivery times for distributors and lower environmental emissions.

### Key Contributions
We introduce a hybrid algorithm, evolving from the Flying Sidekick Traveling Salesman Problem (FSTSP), tailored for the simultaneous deployment of multiple drones. Our paper examines distinct graph structures representing various urban and rural layouts, assessing how adaptations to existing algorithms can optimize delivery strategies. We utilized Google's Distance Matrix API and OR Tools TSP Solver for simulating the performance of our algorithm on different graph structures, highlighting its real-world applicability.



### Repository Content
- Paper: [Final Paper](https://drive.google.com/file/d/1qm-nJ67UYnhKZ-Xmie1mZ4q3v7t-r8oz/view?usp=sharing) — A detailed exposition of our research findings and methodologies.
- Code: The algorithms and data analysis scripts used in our study, showcasing our heuristic approach to drone scheduling.
- Models: The constructed models we used to examine performance on different graph structures. 

### References
- G. Clarke and J. W. Wright. Scheduling of vehicles from a central depot to a number of delivery points.
_Operations Research_, 12(4):568–581, 1964.
- Vincent Furnon and Laurent Perron. OR-Tools routing library.
- Saswata Jana and Partha Sarathi Mandal. Approximation algorithms for drone delivery scheduling
problem. In David Mohaisen and Thomas Wies, editors, _Networked Systems_, pages 125–140, Cham, 2023. Springer Nature Switzerland.
- Chase C. Murray and Amanda G. Chu. The flying sidekick traveling salesman problem: Optimization of
drone-assisted parcel delivery. _Transportation Research Part C: Emerging Technologies_, 54:86–109, 2015.
