Feature: run the cli,
  call the help command,
  exit the cli

  Scenario: run the cli
     Given we have mycli installed
      when we run mycli
      then we see mycli prompt

  Scenario: run "\?" command
     Given we have mycli installed
      when we run mycli
      and we wait for prompt
      and we send "\?" command
      then we see help output

  Scenario: run the cli and exit
     Given we have mycli installed
      when we run mycli
      and we wait for prompt
      and we send "ctrl + d"
      then mycli exits
