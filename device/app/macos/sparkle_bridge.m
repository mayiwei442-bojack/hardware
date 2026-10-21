#import <Foundation/Foundation.h>
#import <Sparkle/Sparkle.h>
#include <stdbool.h>

static SPUStandardUpdaterController *keyboardUpdaterController;

bool keyboard_sparkle_is_enabled(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"keyboard updater configuration must be read on the main thread");
        return false;
    }
    return [NSBundle.mainBundle.infoDictionary[@"keyboardAutomaticUpdates"] boolValue];
}

bool keyboard_sparkle_start(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"keyboard updater must start on the main thread");
        return false;
    }

    NSDictionary *info = NSBundle.mainBundle.infoDictionary;
    if (!keyboard_sparkle_is_enabled()) {
        return false;
    }

    NSString *feedURL = info[@"SUFeedURL"];
    NSString *publicKey = info[@"SUPublicEDKey"];
    if (![feedURL isKindOfClass:NSString.class] || feedURL.length == 0 ||
        ![publicKey isKindOfClass:NSString.class] || publicKey.length == 0 ||
        ![info[@"SURequireSignedFeed"] boolValue] ||
        ![info[@"SUVerifyUpdateBeforeExtraction"] boolValue]) {
        NSLog(@"keyboard updater is disabled because its signed feed is not configured");
        return false;
    }

    if (keyboardUpdaterController == nil) {
        keyboardUpdaterController = [[SPUStandardUpdaterController alloc]
            initWithStartingUpdater:YES
                 updaterDelegate:nil
              userDriverDelegate:nil];
    }
    return keyboardUpdaterController != nil;
}

bool keyboard_sparkle_can_check_for_updates(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"keyboard updater checks must run on the main thread");
        return false;
    }
    return keyboardUpdaterController != nil &&
           keyboardUpdaterController.updater.canCheckForUpdates;
}

bool keyboard_sparkle_session_in_progress(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"keyboard updater state must be read on the main thread");
        return false;
    }
    return keyboardUpdaterController != nil &&
           keyboardUpdaterController.updater.sessionInProgress;
}

bool keyboard_sparkle_check_for_updates(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"keyboard updater checks must run on the main thread");
        return false;
    }
    if (keyboardUpdaterController == nil ||
        !keyboardUpdaterController.updater.canCheckForUpdates) {
        return false;
    }
    [keyboardUpdaterController checkForUpdates:nil];
    return true;
}
