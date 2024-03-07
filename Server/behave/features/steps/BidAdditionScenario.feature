Feature: User adds a bid

    Scenario: User adds a bid
        Given I am on the "Stock" page
        When I log in
        And I fill in "Amount" with "20"
        And I fill in "Price" with "100"
        And I press "Add Bid"
        Then I should see "Bid was successfully added"
        And I should see "20"
        And I should see "100"

