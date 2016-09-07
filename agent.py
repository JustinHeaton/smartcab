import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import defaultdict

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
    
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
    # TODO: Initialize any additional variables here
        self.actions = ['right','left','forward',None]
        self.Q = defaultdict(int)
        self.alpha = .5
        self.gamma = 0
        self.epsilon = .05
        self.total_reward = 0
        self.success = 0
        self.trials = 0
        self.penalty = 0
    
    def reset(self, destination=None):
        self.planner.route_to(destination)
    # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None
        
    
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # TODO: Update state
        input_items = inputs.items()
        self.state = (input_items[0], input_items[1], input_items[3], self.next_waypoint)
        state = self.state
        
        # TODO: Select action according to your policy
        legal_actions = []
        if inputs['light'] == 'red':
            if inputs['oncoming'] != 'left' and inputs['left'] != 'forward':
                legal_actions = ['right', None]
        else:
            if inputs['oncoming'] == 'forward':
                legal_actions = [ 'forward','right']
            else:
                legal_actions = ['right','forward', 'left']
        
        max_Q = -float("inf")
        best_action = None
        for action in legal_actions:
            Q = self.Q[(state, action)]
            if Q > max_Q:
                max_Q = Q
                best_action = action
        
        if random.random() < self.epsilon: # Take a random action (epsilon * 100)% of the time.
            action = random.choice(self.actions)
        else:
            if best_action != None:
                action = best_action
            else:
                if legal_actions != []:
                    if self.next_waypoint in legal_actions:
                        action = self.next_waypoint # Move in direction of destination
                    else:
                        action = None
                else: action = None #There are no legal actions
        
        # Execute action and get reward
        reward = self.env.act(self, action)
        self.total_reward += reward
        if reward >= 10:
            self.success += 1
        if reward < 0:
            self.penalty += 1
        
        # TODO: Learn policy based on state, action, reward
        self.Q[(state, action)]= (1 - self.alpha) * self.Q[(state, action)] + self.alpha * reward
        self.trials += 1
        self.epsilon *= .99 #Decay the epsilon value so that as the model learns, it will explore less
        if self.trials >= 50:
            self.epsilon == 0
        
        
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, total reward = {}, successful trials = {}, number of penalties = {}".format(deadline, inputs, action, self.total_reward, self.success, self.penalty)
        

def run():
    """Run the agent for a finite number of trials."""
    
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials
    
    # Now simulate it
    sim = Simulator(e, update_delay=0.01, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    
    sim.run(n_trials=100)  # run for a specified number of trials
# NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()