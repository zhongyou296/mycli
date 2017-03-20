Feature: I/O commands

  Scenario: edit sql in file with external editor
     Given we have mycli installed
      when we run mycli
      and we wait for prompt
      and we start external editor providing a file name
      and we type sql in the editor
      and we exit the editor
      then we see the sql in prompt
