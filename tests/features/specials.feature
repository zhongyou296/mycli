Feature: Special commands

  @wip
  Scenario: run refresh command
     Given we have mycli installed
      when we run mycli
      and we wait for prompt
      and we refresh completions
      and we wait for prompt
      then we see completions refresh started
