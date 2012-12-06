package com.psikon;

import com.psikon.parsers.W;

import info.bliki.wiki.model.Configuration;
import info.bliki.wiki.model.WikiModel;

/**
 * Custom WikiModel
 * 
 * This is just boilerplate to get gwtwiki to use a custom
 * template function.
 * 
 * @see W
 */
public class WikiNewsModel extends WikiModel {

	static {
		Configuration.DEFAULT_CONFIGURATION.addTemplateFunction("w", W.CONST);
	}
	
	public WikiNewsModel(String imageBaseURL, String linkBaseURL) {
		super(imageBaseURL, linkBaseURL);
	}
}
