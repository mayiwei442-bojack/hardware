#import <Foundation/Foundation.h>
#import <Sparkle/Sparkle.h>
#include <stdbool.h>

static SPUStandardUpdaterController *macropadUpdaterController;

bool keyboard_sparkle_is_enabled(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"MacroPad updater configuration must be read on the main thread");
        return false;
    }
    return [NSBundle.mainBundle.bundleIdentifier isEqualToString:@"io.macropad.desktop"] &&
           [NSBundle.mainBundle.infoDictionary[@"MacroPadAutomaticUpdates"] boolValue];
}

bool keyboard_sparkle_start(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"MacroPad updater must start on the main thread");
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
        NSLog(@"MacroPad updater is disabled because its signed feed is not configured");
        return false;
    }

    NSURL *feed = [NSURL URLWithString:feedURL];
    NSData *decodedKey = [[NSData alloc] initWithBase64EncodedString:publicKey options:0];
    if (![feed.scheme.lowercaseString isEqualToString:@"https"] || feed.host.length == 0 ||
        feed.user != nil || feed.password != nil || feed.fragment != nil || decodedKey.length != 32) {
        NSLog(@"MacroPad updater is disabled because the feed or public key is invalid");
        return false;
    }

    if (macropadUpdaterController == nil) {
        macropadUpdaterController = [[SPUStandardUpdaterController alloc]
            initWithStartingUpdater:YES
                 updaterDelegate:nil
              userDriverDelegate:nil];
    }
    return macropadUpdaterController != nil;
}

bool keyboard_sparkle_can_check_for_updates(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"MacroPad updater checks must run on the main thread");
        return false;
    }
    return macropadUpdaterController != nil &&
           macropadUpdaterController.updater.canCheckForUpdates;
}

bool keyboard_sparkle_session_in_progress(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"MacroPad updater state must be read on the main thread");
        return false;
    }
    return macropadUpdaterController != nil &&
           macropadUpdaterController.updater.sessionInProgress;
}

bool keyboard_sparkle_check_for_updates(void) {
    if (![NSThread isMainThread]) {
        NSLog(@"MacroPad updater checks must run on the main thread");
        return false;
    }
    if (macropadUpdaterController == nil ||
        !macropadUpdaterController.updater.canCheckForUpdates) {
        return false;
    }
    [macropadUpdaterController checkForUpdates:nil];
    return true;
}
