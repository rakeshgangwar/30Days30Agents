#!/usr/bin/env python3
"""
Command Line Interface for the Task Automation Agent
"""

import asyncio
import argparse
import sys
import json
from main import TaskAutomationAgent

async def interactive_automation_creation(agent, description):
    """
    Handle interactive automation creation with parameter collection.
    
    Args:
        agent: TaskAutomationAgent instance
        description: Initial automation description
        
    Returns:
        Final result of automation creation
    """
    # First attempt to create the automation
    result = await agent.create_automation(description)
    
    # Check if the result indicates missing information
    if "Your automation request needs more information" in result:
        print(result)
        print("\nLet's collect the missing information:")
        
        # In a real CLI, we would parse the missing parameters and prompt for each one
        # For now, we'll just ask for a more detailed description
        more_details = input("\nPlease provide a more detailed description with the missing information: ")
        
        # Create the automation with the enhanced description
        enhanced_description = f"{description} with the following details: {more_details}"
        result = await agent.create_automation(enhanced_description)
    
    return result

async def main():
    """Main function for the CLI"""
    parser = argparse.ArgumentParser(description='Task Automation Agent CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Process request command
    process_parser = subparsers.add_parser('process', help='Process a general request')
    process_parser.add_argument('request', help='Natural language request to process')
    
    # List hives command
    subparsers.add_parser('list-hives', help='List available hives')
    
    # Create automation command
    create_parser = subparsers.add_parser('create', help='Create a new automation')
    create_parser.add_argument('description', help='Natural language description of the automation to create')
    create_parser.add_argument('--non-interactive', action='store_true', 
                              help='Skip interactive parameter collection')
    
    # Analyze automation requirements command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze automation requirements')
    analyze_parser.add_argument('description', help='Natural language description of the automation to analyze')
    
    # List automations command
    subparsers.add_parser('list-automations', help='List current automations')
    
    # Delete automation command
    delete_parser = subparsers.add_parser('delete', help='Delete an automation')
    delete_parser.add_argument('id', help='ID of the automation to delete')
    
    # Trigger action command
    trigger_parser = subparsers.add_parser('trigger', help='Trigger a manual action')
    trigger_parser.add_argument('bee_id', help='ID of the bee to trigger the action on')
    trigger_parser.add_argument('action_name', help='Name of the action to trigger')
    trigger_parser.add_argument('--options', help='JSON string of options for the action')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    agent = TaskAutomationAgent()
    
    if args.command == 'process':
        result = await agent.process_request(args.request)
        print(result)
    
    elif args.command == 'list-hives':
        result = await agent.list_available_hives()
        print(result)
    
    elif args.command == 'create':
        if args.non_interactive:
            result = await agent.create_automation(args.description, interactive=False)
        else:
            result = await interactive_automation_creation(agent, args.description)
        print(result)
    
    elif args.command == 'analyze':
        requirements = await agent.analyze_automation_requirements(args.description)
        print(json.dumps(requirements, indent=2))
    
    elif args.command == 'list-automations':
        result = await agent.list_current_automations()
        print(result)
    
    elif args.command == 'delete':
        result = await agent.delete_automation(args.id)
        print(result)
    
    elif args.command == 'trigger':
        options = json.loads(args.options) if args.options else None
        result = await agent.trigger_manual_action(args.bee_id, args.action_name, options)
        print(result)

if __name__ == '__main__':
    asyncio.run(main())
